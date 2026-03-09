from setuptools import find_packages, setup

setup(
    name='notificator',
    version='0.4.0',
    keywords=['notice', 'notificator', 'bark', 'sms', 'mail', 'webhook'],
    description='Notificator SDK with AdminClient and Sender Notificator',
    long_description='Developer-friendly SDK for admin management and unified multi-channel sending.',
    long_description_content_type='text/markdown',
    license='MIT Licence',
    url='https://github.com/Jyonn/notificator',
    author='Jyonn Liu',
    author_email='i@6-79.cn',
    platforms='any',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
)
