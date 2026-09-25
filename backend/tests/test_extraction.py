from app.llm.mock_provider import MockLLMProvider

def test_extract_full_name():
    extracted = MockLLMProvider.extract_information("My name is Jane Smith", {})
    assert extracted.full_name == "Jane Smith"

def test_extract_multiple_fields_one_message():
    user_msg = "I don't have children and I want my brother James to be my executor"
    extracted = MockLLMProvider.extract_information(user_msg, {})
    assert extracted.has_children is False
    assert extracted.children == []
    assert extracted.executor_name == "James"
    assert extracted.executor_relationship == "brother"

def test_extract_unclear_information():
    user_msg = "My executor is maybe my brother Rahul"
    extracted = MockLLMProvider.extract_information(user_msg, {})
    assert extracted.certainty == "uncertain"
    assert extracted.executor_name == "Rahul"
    assert extracted.executor_relationship == "brother"

def test_generate_response_does_not_repeat_captured():
    missing = ["home_address", "covers_worldwide_assets"]
    updated = ["full_name"]
    response = MockLLMProvider.generate_response(missing, updated, [], [])
    assert "home_address" in response or "address" in response.lower()
    assert "full_name" not in response  # should ask about next missing field
