from setuptools import setup, find_packages


def main():
    setup(
        name="cpmdparser",
        version="0.1",
        description="NOMAD parser implementation for CPMD.",
        author="Lauri Himanen",
        author_email="lauri.himanen@aalto.fi",
        license="GPL3",
        package_dir={'': 'parser/parser-cpmd'},
        packages=find_packages(),
        install_requires=[
            'nomadcore',
        ],
    )

if __name__ == "__main__":
    main()
