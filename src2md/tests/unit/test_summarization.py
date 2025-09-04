"""
Unit tests for code summarization strategies.
"""
import pytest
from pathlib import Path
from src2md.strategies.summarization import (
    SummarizationStrategy,
    SummarizationConfig,
    SummarizationLevel,
    PythonSummarizer,
    JavaScriptSummarizer,
    ConfigSummarizer,
    TestSummarizer,
    DocumentationSummarizer
)


class TestPythonSummarizer:
    """Test Python code summarization."""
    
    @pytest.fixture
    def python_code(self):
        return '''"""
Module for data processing utilities.
"""
import os
import json
from typing import List, Dict

class DataProcessor:
    """Process and transform data."""
    
    def __init__(self, config: Dict):
        """Initialize with configuration."""
        self.config = config
        self._cache = {}
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        Process a list of data items.
        
        Args:
            data: List of data dictionaries
            
        Returns:
            Processed data list
        """
        result = []
        for item in data:
            processed = self._transform(item)
            if processed:
                result.append(processed)
        return result
    
    def _transform(self, item: Dict) -> Dict:
        """Transform a single item."""
        # Complex transformation logic
        transformed = {}
        for key, value in item.items():
            if key.startswith('_'):
                continue
            transformed[key.upper()] = str(value)
        return transformed

def load_data(file_path: str) -> List[Dict]:
    """Load data from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(data: List[Dict], file_path: str):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
'''
    
    def test_minimal_summarization(self, python_code):
        """Test minimal level summarization."""
        config = SummarizationConfig(level=SummarizationLevel.MINIMAL)
        summarizer = PythonSummarizer(config)
        
        summary = summarizer.summarize(python_code)
        
        assert "class DataProcessor" in summary
        assert "def process()" in summary
        assert "def load_data()" in summary
        assert "def save_data()" in summary
        assert "_transform" not in summary  # Private method excluded
    
    def test_outline_summarization(self, python_code):
        """Test outline level summarization."""
        config = SummarizationConfig(level=SummarizationLevel.OUTLINE)
        summarizer = PythonSummarizer(config)
        
        summary = summarizer.summarize(python_code)
        
        assert "class DataProcessor:" in summary
        assert "def __init__(self, config):" in summary
        assert "def process(self, data):" in summary
        assert "..." in summary
        assert len(summary) < len(python_code) / 2
    
    def test_docstring_summarization(self, python_code):
        """Test docstring level summarization."""
        config = SummarizationConfig(
            level=SummarizationLevel.DOCSTRINGS,
            preserve_docstrings=True
        )
        summarizer = PythonSummarizer(config)
        
        summary = summarizer.summarize(python_code)
        
        assert "Process and transform data" in summary
        assert "def process" in summary
        assert "Process a list of data items" in summary
        assert "import json" in summary  # Imports preserved
    
    def test_preserve_imports(self, python_code):
        """Test import preservation."""
        config = SummarizationConfig(
            level=SummarizationLevel.MINIMAL,
            preserve_imports=True
        )
        summarizer = PythonSummarizer(config)
        
        summary = summarizer.summarize(python_code)
        
        assert "import os" in summary
        assert "import json" in summary
        assert "from typing import List, Dict" in summary
    
    def test_invalid_python(self):
        """Test handling of invalid Python code."""
        config = SummarizationConfig()
        summarizer = PythonSummarizer(config)
        
        invalid_code = "def broken_function(\n    pass"
        summary = summarizer.summarize(invalid_code)
        
        # Should fall back to regex-based summarization
        assert "def broken_function" in summary


class TestJavaScriptSummarizer:
    """Test JavaScript code summarization."""
    
    @pytest.fixture
    def javascript_code(self):
        return '''import React from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';

class DataService {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.cache = new Map();
    }
    
    async fetchData(endpoint) {
        if (this.cache.has(endpoint)) {
            return this.cache.get(endpoint);
        }
        
        const response = await axios.get(`${this.apiUrl}/${endpoint}`);
        this.cache.set(endpoint, response.data);
        return response.data;
    }
}

const UserList = ({ users }) => {
    const [filteredUsers, setFilteredUsers] = useState(users);
    
    useEffect(() => {
        setFilteredUsers(users.filter(u => u.active));
    }, [users]);
    
    return (
        <div className="user-list">
            {filteredUsers.map(user => (
                <UserCard key={user.id} user={user} />
            ))}
        </div>
    );
};

function processData(data) {
    return data.map(item => ({
        ...item,
        processed: true
    }));
}

export { DataService, UserList, processData };
'''
    
    def test_javascript_summarization(self, javascript_code):
        """Test JavaScript summarization."""
        config = SummarizationConfig()
        summarizer = JavaScriptSummarizer(config)
        
        summary = summarizer.summarize(javascript_code)
        
        assert "class DataService" in summary
        assert "function processData" in summary
        assert "import React" in summary
    
    def test_react_component_detection(self):
        """Test React component detection."""
        config = SummarizationConfig()
        summarizer = JavaScriptSummarizer(config)
        
        react_code = '''
const Button = ({ onClick, label }) => {
    return <button onClick={onClick}>{label}</button>;
};

function Card({ title, children }) {
    return (
        <div className="card">
            <h2>{title}</h2>
            {children}
        </div>
    );
}
'''
        summary = summarizer.summarize(react_code, file_path=Path("component.jsx"))
        
        assert "Component: Button" in summary
        assert "Component: Card" in summary


class TestConfigSummarizer:
    """Test configuration file summarization."""
    
    def test_json_summarization(self):
        """Test JSON config summarization."""
        config = SummarizationConfig()
        summarizer = ConfigSummarizer(config)
        
        json_content = '''{
    "name": "my-project",
    "version": "1.0.0",
    "scripts": {
        "build": "webpack",
        "test": "jest",
        "lint": "eslint ."
    },
    "dependencies": {
        "react": "^18.0.0",
        "axios": "^1.0.0"
    },
    "devDependencies": {
        "webpack": "^5.0.0",
        "jest": "^29.0.0"
    }
}'''
        
        summary = summarizer.summarize(json_content, file_path=Path("package.json"))
        
        assert "name: my-project" in summary
        assert "version: 1.0.0" in summary
        assert "scripts:" in summary
        assert "dependencies:" in summary
    
    def test_yaml_summarization(self):
        """Test YAML config summarization."""
        config = SummarizationConfig()
        summarizer = ConfigSummarizer(config)
        
        yaml_content = '''
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: secret
'''
        
        summary = summarizer.summarize(yaml_content, file_path=Path("docker-compose.yml"))
        
        assert "version: ..." in summary or "YAML configuration" in summary


class TestTestSummarizer:
    """Test summarization of test files."""
    
    def test_python_test_summarization(self):
        """Test Python test file summarization."""
        config = SummarizationConfig()
        summarizer = TestSummarizer(config)
        
        test_content = '''
import pytest

class TestUserService:
    def test_create_user(self):
        """Test user creation."""
        pass
    
    def test_delete_user(self):
        """Test user deletion."""
        pass
    
def test_authentication():
    """Test authentication flow."""
    pass
'''
        
        summary = summarizer.summarize(test_content)
        
        assert "TestUserService" in summary
        assert "test_create_user" in summary
        assert "test_delete_user" in summary
        assert "test_authentication" in summary


class TestSummarizationStrategy:
    """Test the main summarization strategy orchestrator."""
    
    def test_file_type_detection(self):
        """Test that correct summarizer is selected."""
        strategy = SummarizationStrategy()
        
        # Python file
        assert strategy.can_summarize(Path("test.py"))
        
        # JavaScript file
        assert strategy.can_summarize(Path("app.js"))
        
        # Config file
        assert strategy.can_summarize(Path("config.json"))
        
        # Unknown file
        assert not strategy.can_summarize(Path("unknown.xyz"))
    
    def test_target_ratio(self):
        """Test compression ratio targeting."""
        config = SummarizationConfig(target_compression_ratio=0.2)
        strategy = SummarizationStrategy(config)
        
        long_content = "def func():\n    pass\n" * 100
        
        summary = strategy.summarize(Path("test.py"), long_content, target_ratio=0.1)
        
        # Should be significantly shorter
        assert len(summary) < len(long_content) * 0.5
    
    def test_fallback_for_unknown_files(self):
        """Test fallback behavior for unknown file types."""
        strategy = SummarizationStrategy()
        
        content = "Some unknown content\n" * 50
        summary = strategy.summarize(Path("unknown.xyz"), content, target_ratio=0.2)
        
        assert "truncated" in summary or len(summary) < len(content)