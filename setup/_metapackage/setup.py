import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-scholarship",
    description="Meta package for open-synergy-ssi-school-scholarship Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_school_scholarship',
        'odoo14-addon-ssi_school_scholarship_deduction',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
