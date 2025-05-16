from setuptools import setup, find_packages

def read_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#') and not line.startswith('-r')]

# Read requirements
install_requires = read_requirements('requirements.txt')
dev_requires = read_requirements('requirements-dev.txt')

setup(
    name='meal-planner',
    version='0.1.0',
    author='Yoshika Govender',
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
    python_requires='>=3.10',
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
)