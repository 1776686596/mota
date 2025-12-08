"""配置管理器 - 持久化保存 API 配置

支持两种配置来源：
1. 后台环境变量配置（供免费用户使用）
2. 用户自定义配置（优先级更高）
"""

import json
import os
from pathlib import Path


class ConfigManager:
    """配置管理器
    
    配置优先级：用户配置 > 环境变量配置 > 默认配置
    """
    
    # 环境变量名称
    ENV_BASE_URL = "SCIPLOT_LLM_BASE_URL"
    ENV_API_KEY = "SCIPLOT_LLM_API_KEY"
    ENV_MODEL = "SCIPLOT_LLM_MODEL"
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self._default_config()
        return self._default_config()
    
    def _get_env_config(self) -> dict:
        """从环境变量获取后台配置"""
        return {
            "base_url": os.getenv(self.ENV_BASE_URL, ""),
            "api_key": os.getenv(self.ENV_API_KEY, ""),
            "model": os.getenv(self.ENV_MODEL, "")
        }
    
    def has_backend_config(self) -> bool:
        """检查是否有后台环境变量配置"""
        env_config = self._get_env_config()
        return bool(env_config.get("api_key"))
    
    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "llm": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-3.5-turbo"
            },
            "app": {
                "default_style": "Nature",
                "default_format": "png"
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_llm_config(self) -> dict:
        """获取用户 LLM 配置（不包含环境变量）"""
        return self.config.get("llm", self._default_config()["llm"])
    
    def get_effective_llm_config(self) -> dict:
        """获取有效的 LLM 配置
        
        优先级：用户配置 > 环境变量配置 > 默认配置
        
        Returns:
            dict: 包含 base_url, api_key, model 的配置字典
        """
        user_config = self.get_llm_config()
        env_config = self._get_env_config()
        default_config = self._default_config()["llm"]
        
        # 如果用户配置了 API Key，使用用户配置
        if user_config.get("api_key"):
            return user_config
        
        # 否则尝试使用环境变量配置
        if env_config.get("api_key"):
            return {
                "base_url": env_config.get("base_url") or default_config["base_url"],
                "api_key": env_config.get("api_key"),
                "model": env_config.get("model") or default_config["model"]
            }
        
        # 最后返回用户配置（可能为空）
        return user_config
    
    def is_using_backend_config(self) -> bool:
        """检查当前是否使用后台配置
        
        Returns:
            bool: 如果用户没有配置 API Key 且后台有配置，返回 True
        """
        user_config = self.get_llm_config()
        return not user_config.get("api_key") and self.has_backend_config()
    
    def update_llm_config(self, base_url: str = None, api_key: str = None, model: str = None):
        """更新 LLM 配置"""
        llm_config = self.config.get("llm", {})
        
        if base_url is not None:
            llm_config["base_url"] = base_url
        if api_key is not None:
            llm_config["api_key"] = api_key
        if model is not None:
            llm_config["model"] = model
        
        self.config["llm"] = llm_config
        return self.save_config()
    
    def get_app_config(self) -> dict:
        """获取应用配置"""
        return self.config.get("app", self._default_config()["app"])
    
    def update_app_config(self, **kwargs):
        """更新应用配置"""
        app_config = self.config.get("app", {})
        app_config.update(kwargs)
        self.config["app"] = app_config
        return self.save_config()