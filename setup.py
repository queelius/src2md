from setuptools import setup, find_packages

setup(
    name='src2md',
    version='0.8.0',
    author='Alex Towell',
    author_email='lex@example.com',
    description='A tool to convert source code directories into Markdown documentation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/queelius/src2md',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pypandoc',
        'pathspec',
    ],
    entry_points={
        'console_scripts': [
            'src2md=src2md.cli:main',
        ],
    },
)
