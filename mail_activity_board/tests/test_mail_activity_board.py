# Copyright 2018 David Juaneda - <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestMailActivityBoardMethods(TransactionCase):

    def setUp(self):
        super(TestMailActivityBoardMethods, self).setUp()
        # Set up activities

        # Create a user as 'Crm Salesman' and added few groups
        self.employee = self.env['res.users'].create({
            'company_id': self.env.ref("base.main_company").id,
            'name': "Employee",
            'login': "csu",
            'email': "crmuser@yourcompany.com",
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })

        # lead_model_id = self.env['ir.model']._get('crm.lead').id
        partner_model_id = self.env['ir.model']._get('res.partner').id

        ActivityType = self.env['mail.activity.type']
        self.activity1 = ActivityType.create({
            'name': 'Initial Contact',
            'days': 5,
            'summary': 'ACT 1 : Presentation, barbecue, ... ',
            'res_model_id': partner_model_id,
        })
        self.activity2 = ActivityType.create({
            'name': 'Call for Demo',
            'days': 6,
            'summary': 'ACT 2 : I want to show you my ERP !',
            'res_model_id': partner_model_id,
        })
        self.activity3 = ActivityType.create({
            'name': 'Celebrate the sale',
            'days': 3,
            'summary': 'ACT 3 : '
                       'Beers for everyone because I am a good salesman !',
            'res_model_id': partner_model_id,
        })

        # I create an opportunity, as employee
        self.partner_client = self.env.ref("base.res_partner_1")

        self.act1 = self.env['mail.activity'].sudo().create({
            'activity_type_id': self.activity3.id,
            'note': 'Partner activity 1.',
            'res_id': self.partner_client.id,
            'res_model_id': partner_model_id,
            'user_id': self.employee.id
        })
        self.act2 = self.env['mail.activity'].sudo().create({
            'activity_type_id': self.activity2.id,
            'note': 'Partner activity 2.',
            'res_id': self.partner_client.id,
            'res_model_id': partner_model_id,
            'user_id': self.employee.id
        })
        self.act3 = self.env['mail.activity'].sudo().create({
            'activity_type_id': self.activity3.id,
            'note': 'Partner activity 3.',
            'res_id': self.partner_client.id,
            'res_model_id': partner_model_id,
            'user_id': self.employee.id
        })

    def get_view(self, activity):
        action = activity.open_origin()
        result = self.env[action.get('res_model')]\
            .load_views(action.get('views'))
        return result.get('fields_views').get(action.get('view_mode'))

    def test_open_origin_res_partner(self):
        """ This test case checks
                - If the method redirects to the form view of the correct one
                of an object of the 'res.partner' class to which the activity
                belongs.
        """
        # Id of the form view for the class 'crm.lead', type 'lead'
        form_view_partner_id = self.env.ref('base.view_partner_form').id

        # Id of the form view return open_origin()
        view = self.get_view(self.act1)

        # Check the next view is correct
        self.assertEqual(form_view_partner_id, view.get('view_id'))

        # Id of the form view return open_origin()
        view = self.get_view(self.act2)

        # Check the next view is correct
        self.assertEqual(form_view_partner_id, view.get('view_id'))

        # Id of the form view return open_origin()
        view = self.get_view(self.act3)

        # Check the next view is correct
        self.assertEqual(form_view_partner_id, view.get('view_id'))

    def test_redirect_to_activities(self):
        """ This test case checks
                - if the method returns the correct action,
                - if the correct activities are shown.
        """
        action_id = self.env.ref(
            'mail_activity_board.open_boards_activities').id
        action = self.partner_client\
            .redirect_to_activities(**{'id': self.partner_client.id})
        self.assertEqual(action.get('id'), action_id)

        kwargs = {
            'groupby': [
                "activity_type_id"
            ]
        }
        kwargs['domain'] = action.get('domain')

        result = self.env[action.get('res_model')]\
            .load_views(action.get('views'))
        fields = result.get('fields_views').get('kanban').get('fields')
        kwargs['fields'] = list(fields.keys())

        result = self.env['mail.activity'].read_group(**kwargs)

        acts = []
        for group in result:
            records = self.env['mail.activity'].search_read(
                domain=group.get('__domain'), fields=kwargs['fields']
            )
            acts += [id.get('id') for id in records]

        for act in acts:
            self.assertIn(act, self.partner_client.activity_ids.ids)