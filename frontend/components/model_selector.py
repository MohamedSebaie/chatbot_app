import streamlit as st
from typing import Callable, Dict
import logging

logger = logging.getLogger(__name__)

class ModelSelector:
    """Component for model selection and configuration."""
    
    def __init__(self):
        self.models = {
            
            "Llama 3": {
                "id": "llama",
                "description": "Open-source model running locally. Good for privacy-sensitive applications.",
                "color": "green",
                "icon": "🦙"
            },
            "OpenAI GPT": {
                "id": "openai",
                "description": "Powered by OpenAI's GPT model. Best for general purpose tasks and complex reasoning.",
                "color": "blue",
                "icon": "🤖"
            }
        }

    def render(self, on_change: Callable = None) -> str:
        """
        Render model selection component.
        
        Args:
            on_change: Callback function for model change
            
        Returns:
            Selected model ID
        """
        with st.sidebar:
            # st.title("Model Settings")
            
            current_model = st.radio(
                "Select Model",
                options=list(self.models.keys()),
                key="model_selector",
                on_change=on_change if on_change else None,
                format_func=lambda x: f"{self.models[x]['icon']} {x}"
            )
            
            model_info = self.models[current_model]
            
            st.markdown(
                f"""
                <div style='padding: 1rem; border-radius: 0.5rem; 
                background-color: {model_info['color']}20; margin: 1rem 0;'>
                    <h4 style='color: {model_info['color']};'>
                        {model_info['icon']} {current_model}
                    </h4>
                    <p>{model_info['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            return model_info['id']