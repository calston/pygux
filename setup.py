from setuptools import setup, find_packages


setup(
    name="pygux",
    version='0.1',
    url='https://github.com/calston/pygux',
    license='MIT',
    description="Make HMIs easily with PyGame",
    author='Colin Alston',
    author_email='colin.alston@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pygame',
        'pycairo'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
