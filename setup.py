import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name = 'didak',
    packages = ["didak"],
    version = '1.0.28',
    license='MIT',
    description = 'Didak is a simple test case runner, that simulates input and verifies the whether the final output is correct.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Rodney Maniego Jr.',
    author_email = 'rod.maniego23@gmail.com',
    url = 'https://github.com/rmaniego/didak',
    download_url = 'https://github.com/rmaniego/didak/archive/v1.0.tar.gz',
    keywords = ['Python', 'test', 'testcase', 'automation'],
    install_requires=["arkivist", "maguro", "autopep8"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers', 
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6'
)