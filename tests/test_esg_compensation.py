"""Tests for ESG compensation classification pipeline."""

import pytest
from esg_compensation_pipeline_all_in_one import (
    process_proxy_statement,
    tokenize_words,
    count_term_in_text,
    extract_section,
    find_terms_within_distance,
    identify_esg_pay,
    calculate_esg_intensity,
    weighted_esg_score,
    is_greenwashing,
    distinguish_governance_vs_compensation,
    identify_ceo_specific,
    compute_validation_metrics,
)


class TestTextUtilities:
    """Test text processing utilities."""

    def test_tokenize_words(self):
        text = "The CEO's compensation includes ESG-linked metrics."
        tokens = tokenize_words(text)
        assert "ceo's" in tokens or "ceo" in tokens
        assert "compensation" in tokens
        assert "esg" in tokens or "esg-linked" in tokens

    def test_tokenize_words_empty(self):
        assert tokenize_words("") == []
        assert tokenize_words(None) == []

    def test_count_term_in_text(self):
        text = "ESG compensation and ESG metrics are part of ESG strategy."
        count = count_term_in_text(text, "ESG")
        assert count == 3

    def test_count_term_case_insensitive(self):
        text = "esg compensation and ESG metrics"
        count = count_term_in_text(text, "ESG")
        assert count == 2

    def test_find_terms_within_distance(self):
        text = "The annual bonus includes diversity goals and safety metrics near compensation terms."
        matches = find_terms_within_distance(text, "diversity goals", ["compensation", "bonus"], max_distance=20)
        assert len(matches) > 0


class TestSectionExtraction:
    """Test CD&A section extraction."""

    def test_extract_section_basic(self):
        text = """
        Some introduction text.
        Compensation Discussion and Analysis
        This is the CD&A section with important compensation details.
        Executive Officers
        This is another section.
        """
        section = extract_section(text, ["Compensation Discussion and Analysis"])
        assert "CD&A section" in section
        assert len(section) > 0

    def test_extract_section_not_found(self):
        text = "Some text without the target section."
        section = extract_section(text, ["Compensation Discussion and Analysis"])
        assert section == ""

    def test_extract_section_multiple_identifiers(self):
        text = """
        Introduction
        CD&A
        This is the section we want.
        """
        section = extract_section(text, ["Compensation Discussion and Analysis", "CD&A"])
        assert "section we want" in section


class TestESGClassification:
    """Test ESG pay identification logic."""

    def test_identify_esg_pay_tier1(self):
        text = """
        Compensation Discussion and Analysis
        Our executives' compensation includes an ESG-linked compensation component.
        The annual bonus uses an ESG modifier based on sustainability performance.
        """
        cd_and_a = extract_section(text, ["Compensation Discussion and Analysis"])
        result = identify_esg_pay(text, cd_and_a)
        assert result["ESG_PAY"] == 1
        assert result["confidence"] == "high"
        assert result["tier"] == 1
        assert len(result["matched_terms"]) > 0

    def test_identify_esg_pay_tier2(self):
        text = """
        Compensation Discussion and Analysis
        Executive compensation includes climate targets and diversity goals.
        These metrics are tied to the annual incentive plan.
        """
        cd_and_a = extract_section(text, ["Compensation Discussion and Analysis"])
        result = identify_esg_pay(text, cd_and_a)
        # Should match tier 2 if terms are near compensation terms
        assert result["ESG_PAY"] in [0, 1]  # depends on proximity

    def test_identify_esg_pay_no_match(self):
        text = """
        Compensation Discussion and Analysis
        Executive compensation is based on financial performance and operational metrics.
        """
        cd_and_a = extract_section(text, ["Compensation Discussion and Analysis"])
        result = identify_esg_pay(text, cd_and_a)
        assert result["ESG_PAY"] == 0
        assert result["confidence"] == "none"

    def test_identify_esg_pay_missing_section(self):
        result = identify_esg_pay("Some text", "")
        assert result["ESG_PAY"] is None
        assert result["confidence"] == "missing_cd_and_a"


class TestESGIntensity:
    """Test ESG intensity calculation."""

    def test_calculate_esg_intensity(self):
        text = """
        Our compensation plan includes climate targets, diversity goals, and safety performance.
        These metrics are tied to executive pay and incentive compensation.
        """
        result = calculate_esg_intensity(text)
        assert result["ESG_PAY_INTENSITY"] >= 0
        assert "E_count" in result
        assert "S_count" in result
        assert "G_count" in result
        assert result["ESG_PAY_BREADTH"] >= 0

    def test_calculate_esg_intensity_empty(self):
        result = calculate_esg_intensity("")
        assert result["ESG_PAY_INTENSITY"] == 0
        assert result["E_count"] == 0
        assert result["S_count"] == 0
        assert result["G_count"] == 0


class TestWeightedScore:
    """Test weighted ESG scoring."""

    def test_weighted_esg_score(self):
        text = """
        Compensation includes ESG-linked pay with an ESG modifier.
        We also consider sustainability and environmental metrics.
        """
        result = weighted_esg_score(text)
        assert "ESG_PAY_SCORE" in result
        assert result["ESG_PAY_SCORE"] >= 0
        assert "ESG_PAY_weighted_binary" in result

    def test_weighted_esg_score_threshold(self):
        text = """
        Compensation includes ESG-linked compensation and ESG modifier.
        Sustainability metrics are also considered.
        """
        result = weighted_esg_score(text, threshold=2.0)
        # Should exceed threshold with high-confidence terms
        assert result["ESG_PAY_SCORE"] > 2.0
        assert result["ESG_PAY_weighted_binary"] == 1


class TestEdgeCases:
    """Test edge case handling."""

    def test_is_greenwashing(self):
        sentence1 = "We are committed to sustainability."
        sentence2 = "Compensation includes ESG-linked pay and sustainability metrics."
        assert is_greenwashing(sentence1) is True
        assert is_greenwashing(sentence2) is False

    def test_distinguish_governance_vs_compensation(self):
        text1 = "Our board has an ESG committee for oversight."
        text2 = "Executive compensation includes ESG metrics and incentive pay."
        result1 = distinguish_governance_vs_compensation(text1)
        result2 = distinguish_governance_vs_compensation(text2)
        assert result1 == "governance_not_compensation"
        assert result2 == "potential_esg_compensation"

    def test_identify_ceo_specific(self):
        text = "The CEO compensation and named executive officers receive ESG-linked pay."
        result = identify_ceo_specific(text)
        assert result["applies_to_ceo"] is True
        assert result["mentions_neo"] is True


class TestProcessProxyStatement:
    """Test main processing function."""

    def test_process_proxy_statement_with_esg(self):
        proxy_text = """
        Introduction to our company.
        Compensation Discussion and Analysis
        Our CEO and named executive officers receive compensation that includes
        ESG-linked pay. The annual bonus has an ESG modifier based on emissions
        reduction targets and diversity goals. We also use climate targets in our LTIP.
        Other Sections
        More content here.
        """
        result = process_proxy_statement("TEST_FIRM", 2024, proxy_text)
        
        assert result["firm_id"] == "TEST_FIRM"
        assert result["year"] == 2024
        assert result["ESG_PAY"] == 1
        assert result["cd_and_a_found"] is True
        assert result["proxy_available"] is True
        assert len(result["matched_terms"]) > 0
        assert result["applies_to_ceo"] is True
        assert result["mentions_neo"] is True

    def test_process_proxy_statement_without_esg(self):
        proxy_text = """
        Compensation Discussion and Analysis
        Executive compensation is based on financial performance and operational excellence.
        We pay competitive salaries and bonuses based on revenue and profit targets.
        """
        result = process_proxy_statement("TEST_FIRM", 2024, proxy_text)
        
        assert result["ESG_PAY"] == 0
        assert result["cd_and_a_found"] is True

    def test_process_proxy_statement_missing_section(self):
        proxy_text = "Some proxy text without CD&A section."
        result = process_proxy_statement("TEST_FIRM", 2024, proxy_text)
        
        assert result["ESG_PAY"] is None
        assert result["cd_and_a_found"] is False


class TestValidationMetrics:
    """Test validation metric calculation."""

    def test_compute_validation_metrics_perfect(self):
        manual = [1, 0, 1, 0, 1, 1, 0, 0]
        auto = [1, 0, 1, 0, 1, 1, 0, 0]
        metrics = compute_validation_metrics(manual, auto)
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1"] == 1.0
        assert metrics["tp"] == 4
        assert metrics["tn"] == 4
        assert metrics["fp"] == 0
        assert metrics["fn"] == 0

    def test_compute_validation_metrics_mixed(self):
        manual = [1, 0, 1, 0]
        auto = [1, 1, 1, 0]
        metrics = compute_validation_metrics(manual, auto)
        assert metrics["tp"] == 2
        assert metrics["tn"] == 1
        assert metrics["fp"] == 1
        assert metrics["fn"] == 0
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1"] <= 1


class TestIntegration:
    """Integration tests."""

    def test_demo_example(self):
        """Test the demo example from the CLI."""
        demo_text = """
        Compensation Discussion and Analysis
        Our annual incentive plan includes sustainability metrics. The CEO's annual bonus
        is partly tied to emissions reduction targets and diversity goals. The LTIP uses an ESG modifier.
        """
        result = process_proxy_statement("DEMO_CO", 2024, demo_text)
        
        assert result["ESG_PAY"] == 1
        assert result["ESG_PAY_confidence"] == "high"
        assert result["ESG_PAY_tier"] == 1
        assert result["applies_to_ceo"] is True
        assert "ESG modifier" in result["matched_terms"]
        assert result["ESG_PAY_SCORE"] > 0
