import os
import unittest
from typing import Any

from unittest.mock import patch

from litellm.types.utils import ModelResponse

from aider.models import (
    ANTHROPIC_BETA_HEADER,
    Model,
    register_litellm_models,
)


class TestModelsAzureOpenAI(unittest.TestCase):
    def setUp(self):
        """Reset MODEL_SETTINGS before each test"""
        from aider.models import MODEL_SETTINGS

        self._original_settings = MODEL_SETTINGS.copy()

    def tearDown(self):
        """Restore original MODEL_SETTINGS after each test"""
        from aider.models import MODEL_SETTINGS

        MODEL_SETTINGS.clear()
        MODEL_SETTINGS.extend(self._original_settings)

    def test_simple_send_with_retries_removes_reasoning(self):
        # model_settings = ModelSettings()
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        os.environ["AZURE_AI_API_KEY"] = api_key
        model = Model("azure_ai/deepseek-r1")  # This model has remove_reasoning="think"
        model.extra_params = {
          "api_base": "https://aigc0685508828.services.ai.azure.com/models",
          "api_version": "2024-05-01-preview",
        }

        self.assertEqual(model.edit_format, "diff")
        self.assertTrue(model.use_repo_map)
        self.assertTrue(model.examples_as_sys_msg)
        self.assertFalse(model.use_temperature)
        self.assertEqual(model.remove_reasoning, "think")

        messages = [{"role": "user", "content": "hello, world!"}]
        # resp = model.send_completion(messages=messages)
        result: tuple[Any, ModelResponse] = model.send_completion(messages, None, False)
        print(result[1].choices[0].message.content)

    def test_fixture_configures_model(self):
        """Test that model configuration is loaded from fixture metadata"""
        with patch.dict(os.environ, {"AZURE_AI_API_KEY": "sk-test-key"}):
            # Load model metadata from fixture
            from pathlib import Path
            from aider.models import MODEL_SETTINGS
            
            fixture_path = Path(__file__).parent.parent / "fixtures/aider_model_metadata.json"
            register_litellm_models([fixture_path])
            
            # Model name matches entry in aider_model_metadata.json
            model = Model("azure_ai/deepseek-r1")
            
            # Verify settings from fixture are applied
            self.assertEqual(model.edit_format, "diff")
            self.assertTrue(model.use_repo_map)
            self.assertTrue(model.examples_as_sys_msg)
            self.assertFalse(model.use_temperature)
            self.assertEqual(model.remove_reasoning, "think")
            
            # Verify extra_params from fixture are set
            self.assertEqual(model.extra_params["api_base"], "https://aigc0685508828.services.ai.azure.com/models")
            self.assertEqual(model.extra_params["api_version"], "2024-05-01-preview")


if __name__ == "__main__":
    unittest.main()
