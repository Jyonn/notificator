from pathlib import Path

from setuptools import find_packages, setup


BASE_DIR = Path(__file__).resolve().parent
README = (BASE_DIR / 'README.md').read_text(encoding='utf-8')

setup(
    name='notificator',
    version='0.4.1',
    keywords=['notice', 'notificator', 'bark', 'ntfy', 'gotify', 'sms', 'mail', 'webhook'],
    description='Notificator SDK with AdminClient and Sender Notificator',
    long_description=README,
    long_description_content_type='text/markdown',
    license='MIT Licence',
    url='https://github.com/Jyonn/notificator',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
)
