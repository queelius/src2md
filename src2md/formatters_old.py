"""
Output formatters for src2md - convert structured data to various formats.

Supports JSON, JSONL, Markdown, HTML, and plain text output.
"""
import json
from pathlib import Path
from datetime import datetime


def to_json(data, pretty=True, include_content=True):
    """Convert codebase data to JSON format."""
    output_data = data.copy()
    
    if not include_content:
        output_data = _strip_content(output_data)
    
    if pretty:
        return json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        return json.dumps(output_data, ensure_ascii=False)


def to_jsonl(data, include_content=True):
    """Convert codebase data to JSONL format (one JSON object per line)."""
    lines = []
    
    # Metadata line
    lines.append(json.dumps({
        'type': 'metadata',
        'data': data['metadata']
    }))
    
    # Structure line
    lines.append(json.dumps({
        'type': 'structure', 
        'data': data['structure']
    }))
    
    # Statistics line (if present)
    if data.get('statistics'):
        lines.append(json.dumps({
            'type': 'statistics',
            'data': data['statistics']
        }))
    
    # Documentation files
    for doc in data['documentation']:
        doc_data = doc.copy() if include_content else _strip_file_content(doc)
        lines.append(json.dumps({
            'type': 'documentation',
            'data': doc_data
        }))
    
    # Source files
    for src in data['source_files']:
        src_data = src.copy() if include_content else _strip_file_content(src)
        lines.append(json.dumps({
            'type': 'source_file', 
            'data': src_data
        }))
    
    return '\n'.join(lines)


def to_markdown(data, include_toc=True, include_stats=True):
    """Convert codebase data to Markdown format (legacy compatible)."""
    lines = []
    
    # Title
    project_name = data['metadata']['project_name']
    lines.append(f"# {project_name}\n")
    lines.append(f"*Generated on {data['metadata']['generated_at']}*\n")
    
    # Table of Contents
    if include_toc:
        lines.append("## Table of Contents\n")
        lines.append("- [Project Overview](#project-overview)")
        if include_stats and data.get('statistics'):
            lines.append("- [Statistics](#statistics)")
        if data['documentation']:
            lines.append("- [Documentation](#documentation)")
        if data['source_files']:
            lines.append("- [Source Files](#source-files)")
        lines.append("")
    
    # Project Overview
    lines.append("## Project Overview\n")
    lines.append(f"**Project Path:** `{data['metadata']['project_path']}`\n")
    
    # Statistics
    if include_stats and data.get('statistics'):
        lines.append("## Statistics\n")
        stats = data['statistics']
        lines.append(f"- **Total Files:** {stats.get('total_files', 0)}")
        lines.append(f"- **Source Files:** {stats.get('source_files_count', 0)}")
        lines.append(f"- **Documentation Files:** {stats.get('documentation_files_count', 0)}")
        lines.append(f"- **Total Size:** {_format_bytes(stats.get('total_size_bytes', 0))}")
        lines.append(f"- **Project Complexity Score:** {stats.get('project_complexity', 'N/A')}")
        
        if any(lang_stats for lang, lang_stats in stats.items() if isinstance(lang_stats, dict)):
            lines.append("\n**Breakdown by Language:**\n")
            lines.append("| Language | Files | Lines |")
            lines.append("|----------|-------|-------|")
            for lang, lang_stats in sorted(stats.items()):
                if isinstance(lang_stats, dict):
                    lines.append(f"| {lang} | {lang_stats['files']} | {lang_stats['lines']} |")
        lines.append("")

    # Documentation
    if data['documentation']:
        lines.append("## Documentation\n")
        for doc in data['documentation']:
            if doc.get('path'):
                if doc.get('name') == 'README.md':
                    lines.append("### Main README\n")
                else:
                    lines.append(f"### Documentation: `{doc['path']}`\n")
            
            if doc.get('content'):
                lines.append(doc['content'])
            lines.append("\n")

    # Source Files
    if data['source_files']:
        lines.append("## Source Files\n")
        for src in data['source_files']:
            if src.get('path') and src.get('language'):
                lines.append(f"### Source: `{src['path']}` ({src['language']})\n")
            
            if src.get('content'):
                lines.append(f"```{src.get('language', '')}\n{src['content']}\n```")
            lines.append("\n")
            
    return '\n'.join(lines)

def to_html(data, include_stats=True, include_content=True):
    """Convert codebase data to HTML format."""
    import markdown
    
    md_content = to_markdown(data, include_toc=True, include_stats=include_stats)
    html_body = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    
    project_name = data['metadata']['project_name']
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{project_name}</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: auto; }}
            h1, h2, h3 {{ color: #333; }}
            pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            code {{ font-family: monospace; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return html

def to_text(data, include_stats=True, include_content=True):
    """Convert codebase data to plain text format."""
    lines = []
    
    # Title
    project_name = data['metadata']['project_name']
    lines.append(f"Project: {project_name}")
    lines.append(f"Generated: {data['metadata']['generated_at']}\n")
    
    # Statistics
    if include_stats and data.get('statistics'):
        lines.append("--- Statistics ---")
        stats = data['statistics']
        lines.append(f"Total Files: {stats.get('total_files', 0)}")
        lines.append(f"Source Files: {stats.get('source_files_count', 0)}")
        lines.append(f"Documentation Files: {stats.get('documentation_files_count', 0)}")
        lines.append(f"Total Size: {_format_bytes(stats.get('total_size_bytes', 0))}")
        
        if any(lang_stats for lang, lang_stats in stats.items() if isinstance(lang_stats, dict)):
            lines.append("\nBreakdown by Language:")
            for lang, lang_stats in sorted(stats.items()):
                if isinstance(lang_stats, dict):
                    lines.append(f"  - {lang}: {lang_stats['files']} files, {lang_stats['lines']} lines")
        lines.append("")

    # Documentation
    if include_content and data['documentation']:
        lines.append("--- Documentation ---")
        for doc in data['documentation']:
            lines.append(f"File: {doc['path']}")
            if doc.get('content'):
                lines.append(doc['content'])
            lines.append("\n")

    # Source Files
    if include_content and data['source_files']:
        lines.append("--- Source Files ---")
        for src in data['source_files']:
            lines.append(f"File: {src['path']} ({src['language']})")
            if src.get('content'):
                lines.append(src['content'])
            lines.append("\n")
            
    return '\n'.join(lines)


def _format_bytes(size_bytes):
    """Format bytes into a human-readable string."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def _strip_content(data):
    """Remove content from all files in the data structure."""
    if 'documentation' in data:
        for file_data in data['documentation']:
            file_data.pop('content', None)
    if 'source_files' in data:
        for file_data in data['source_files']:
            file_data.pop('content', None)
    return data


def _strip_file_content(file_data):
    """Remove content from a single file dictionary."""
    new_data = file_data.copy()
    new_data.pop('content', None)
    return new_data
