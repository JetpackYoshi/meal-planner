from setuptools import setup, find_packages

setup(
    name='meal-planner',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A meal planner application that manages dietary restrictions and meal compatibility.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/JetpackYoshi/meal-planner',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)