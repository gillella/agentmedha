import pytest
from unittest.mock import MagicMock, patch
from agent_medha.workers.social_media import draft_post, post_linkedin, post_instagram

def test_draft_post_twitter():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "This is a tweet #test"
        
        result = draft_post.invoke({"topic": "Test Topic", "research_notes": "Research notes", "platform": "twitter"})
        
        assert "This is a tweet #test" in result
        # Verify prompt contains twitter specific instructions
        args, _ = mock_instance.generate_content.call_args
        assert "twitter" in args[0].lower()
        assert "280 characters" in args[0]

def test_draft_post_linkedin():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "This is a professional LinkedIn post."
        
        result = draft_post.invoke({"topic": "Test Topic", "research_notes": "Research notes", "platform": "linkedin"})
        
        assert "This is a professional LinkedIn post." in result
        # Verify prompt contains linkedin specific instructions
        args, _ = mock_instance.generate_content.call_args
        assert "linkedin" in args[0].lower()
        assert "professional tone" in args[0].lower()

def test_draft_post_instagram():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content.return_value.text = "Visual caption for Insta!"
        
        result = draft_post.invoke({"topic": "Test Topic", "research_notes": "Research notes", "platform": "instagram"})
        
        assert "Visual caption for Insta!" in result
        # Verify prompt contains instagram specific instructions
        args, _ = mock_instance.generate_content.call_args
        assert "instagram" in args[0].lower()
        assert "visual-first" in args[0].lower()

def test_post_linkedin_mock():
    result = post_linkedin.invoke({"content": "My LinkedIn Content"})
    assert "Successfully posted to LinkedIn (Mocked)" in result

def test_post_instagram_mock():
    result = post_instagram.invoke({"content": "My Insta Content", "image_url": "http://example.com/image.jpg"})
    assert "Successfully posted to Instagram (Mocked)" in result

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_draft_post_twitter()
        print("test_draft_post_twitter PASSED")
        test_draft_post_linkedin()
        print("test_draft_post_linkedin PASSED")
        test_draft_post_instagram()
        print("test_draft_post_instagram PASSED")
        test_post_linkedin_mock()
        print("test_post_linkedin_mock PASSED")
        test_post_instagram_mock()
        print("test_post_instagram_mock PASSED")
    except Exception as e:
        print(f"FAILED: {e}")
