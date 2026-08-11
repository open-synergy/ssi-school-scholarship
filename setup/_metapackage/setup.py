import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-scholarship",
    description="Meta package for open-synergy-ssi-school-scholarship Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_school_scholarship',
        'odoo14-addon-ssi_school_scholarship_admission',
        'odoo14-addon-ssi_school_scholarship_admission_operating_unit',
        'odoo14-addon-ssi_school_scholarship_deduction',
        'odoo14-addon-ssi_school_scholarship_deduction_operating_unit',
        'odoo14-addon-ssi_school_scholarship_disbursement',
        'odoo14-addon-ssi_school_scholarship_disbursement_operating_unit',
        'odoo14-addon-ssi_school_scholarship_operating_unit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
