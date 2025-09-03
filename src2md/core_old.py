"""
Core module for src2md - converts source code directories to structured data.

The main interface returns a dictionary representation of the codebase,
which can then be rendered to various formats (JSON, Markdown, HTML, etc.).
"""
import os
from pathlib import Path
from datetime import datetime
import fnmatch
from dirschema.core import DirectorySerializer
from .utils import default_langs, convert_rst_to_md, get_language_identifier


def analyze_codebase(
    path,
    doc_pat=None,
    src_pat=None,
    ignore_pat=None,
    include_stats=True,
    include_content=True
):
    """
    Analyze a codebase and return structured data.
    
    Args:
        path (str): Path to the source directory
        doc_pat (list): Patterns for documentation files
        src_pat (list): Patterns for source files  
        ignore_pat (list): Patterns for files to ignore
        include_stats (bool): Include code statistics
        include_content (bool): Include file contents
        
    Returns:
        dict: Structured representation of the codebase
    """
    path = Path(path)
    
    # Set defaults
    if doc_pat is None:
        doc_pat = ['*.md', '*.rst']
    if src_pat is None:
        src_pat = [f"*{ext}" for ext in default_langs.keys()]
    if ignore_pat is None:
        ignore_pat = ['.*']

    # Use dirschema to get the directory structure
    serializer = DirectorySerializer(path, include_binary=False, include_hidden=False)
    dir_structure = serializer.serialize()

    # Initialize result structure
    result = {
        'metadata': {
            'project_name': path.name,
            'project_path': str(path.absolute()),
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'patterns': {
                'documentation': doc_pat,
                'source': src_pat,
                'ignore': ignore_pat
            }
        },
        'structure': dir_structure,
        'documentation': [],
        'source_files': [],
        'statistics': {} if include_stats else None
    }

    # Process the structure to categorize files and calculate stats
    _process_node(
        dir_structure,
        result['documentation'],
        result['source_files'],
        result['statistics'],
        doc_pat,
        src_pat,
        include_content
    )

    return result

def _process_node(
    node,
    doc_files,
    source_files,
    stats,
    doc_pat,
    src_pat,
    include_content
):
    """Recursively process nodes from dirschema output."""
    if stats is not None:
        if 'total_files' not in stats:
            stats['total_files'] = 0
        if 'source_files_count' not in stats:
            stats['source_files_count'] = 0
        if 'documentation_files_count' not in stats:
            stats['documentation_files_count'] = 0
        if 'total_size_bytes' not in stats:
            stats['total_size_bytes'] = 0

    if node['type'] == 'directory':
        for child in node.get('children', []):
            _process_node(child, doc_files, source_files, stats, doc_pat, src_pat, include_content)
    elif node['type'] == 'file':
        if stats is not None:
            stats['total_files'] += 1
            stats['total_size_bytes'] += node['size']

        file_info = {
            'name': node['name'],
            'path': node['path'],
            'size': node['size'],
            'mtime': node['mtime'],
        }

        is_doc = any(fnmatch.fnmatch(node['name'], pat) for pat in doc_pat)
        is_src = any(fnmatch.fnmatch(node['name'], pat) for pat in src_pat)

        if is_doc:
            if stats is not None:
                stats['documentation_files_count'] += 1
            if include_content:
                content = node.get('content', '')
                if node['name'].endswith('.rst'):
                    content = convert_rst_to_md(content)
                file_info['content'] = content
            doc_files.append(file_info)
        
        if is_src:
            if stats is not None:
                stats['source_files_count'] += 1
            if include_content:
                file_info['content'] = node.get('content', '')
            
            lang = get_language_identifier(node['name'])
            file_info['language'] = lang
            
            if stats is not None:
                lines = file_info.get('content', '').count('\n') + 1
                if lang not in stats:
                    stats[lang] = {'files': 0, 'lines': 0}
                stats[lang]['files'] += 1
                stats[lang]['lines'] += lines

            source_files.append(file_info)
