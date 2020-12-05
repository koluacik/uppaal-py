from setuptools import setup, find_packages

setup(
        name='uppaal-py',
        version='0.0.1',
        description='UPPAAL wrapper for Python',
        packages=find_packages(),
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        license='MIT',
        author='Deniz Koluaçık',
        author_email='koluacik@disroot.org',
        python_requires='>=3.8',
        install_requires=[
            'networkx'
            ],
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License'
            ]
        )
