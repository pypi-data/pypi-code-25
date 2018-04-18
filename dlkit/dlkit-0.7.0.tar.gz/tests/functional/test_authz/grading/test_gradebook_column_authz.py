"""TestAuthZ implementations of grading.GradebookColumn"""

import datetime
import pytest
from tests.utilities.general import is_never_authz, is_no_authz, uses_cataloging
from dlkit.abstract_osid.authorization import objects as ABCObjects
from dlkit.abstract_osid.authorization import queries as ABCQueries
from dlkit.abstract_osid.authorization.objects import Authorization
from dlkit.abstract_osid.authorization.objects import AuthorizationList
from dlkit.abstract_osid.authorization.objects import Vault as ABCVault
from dlkit.abstract_osid.osid import errors
from dlkit.abstract_osid.osid.objects import OsidCatalogForm, OsidCatalog
from dlkit.abstract_osid.osid.objects import OsidForm
from dlkit.primordium.calendaring.primitives import DateTime
from dlkit.primordium.id.primitives import Id
from dlkit.primordium.type.primitives import Type
from dlkit.runtime import PROXY_SESSION, proxy_example
from dlkit.runtime.managers import Runtime
REQUEST = proxy_example.SimpleRequest()
CONDITION = PROXY_SESSION.get_proxy_condition()
CONDITION.set_http_request(REQUEST)
PROXY = PROXY_SESSION.get_proxy(CONDITION)

JANE_REQUEST = proxy_example.SimpleRequest(username='jane_doe')
JANE_CONDITION = PROXY_SESSION.get_proxy_condition()
JANE_CONDITION.set_http_request(JANE_REQUEST)
JANE_PROXY = PROXY_SESSION.get_proxy(JANE_CONDITION)

LOOKUP_GRADEBOOK_COLUMN_FUNCTION_ID = Id(**{'identifier': 'lookup', 'namespace': 'grading.GradebookColumn', 'authority': 'ODL.MIT.EDU'})
SEARCH_GRADEBOOK_COLUMN_FUNCTION_ID = Id(**{'identifier': 'search', 'namespace': 'grading.GradebookColumn', 'authority': 'ODL.MIT.EDU'})
CREATE_GRADEBOOK_COLUMN_FUNCTION_ID = Id(**{'identifier': 'create', 'namespace': 'grading.GradebookColumn', 'authority': 'ODL.MIT.EDU'})
DELETE_GRADEBOOK_COLUMN_FUNCTION_ID = Id(**{'identifier': 'delete', 'namespace': 'grading.GradebookColumn', 'authority': 'ODL.MIT.EDU'})
ASSIGN_GRADEBOOK_COLUMN_FUNCTION_ID = Id(**{'identifier': 'assign', 'namespace': 'grading.GradebookColumnGradebook', 'authority': 'ODL.MIT.EDU'})
CREATE_GRADEBOOK_FUNCTION_ID = Id(**{'identifier': 'create', 'namespace': 'grading.Gradebook', 'authority': 'ODL.MIT.EDU'})
DELETE_GRADEBOOK_FUNCTION_ID = Id(**{'identifier': 'delete', 'namespace': 'grading.Gradebook', 'authority': 'ODL.MIT.EDU'})
LOOKUP_GRADEBOOK_FUNCTION_ID = Id(**{'identifier': 'lookup', 'namespace': 'grading.Gradebook', 'authority': 'ODL.MIT.EDU'})
ACCESS_GRADEBOOK_HIERARCHY_FUNCTION_ID = Id(**{'identifier': 'access', 'namespace': 'grading.Gradebook', 'authority': 'ODL.MIT.EDU'})
MODIFY_GRADEBOOK_HIERARCHY_FUNCTION_ID = Id(**{'identifier': 'modify', 'namespace': 'grading.Gradebook', 'authority': 'ODL.MIT.EDU'})
ROOT_QUALIFIER_ID = Id('grading.Gradebook%3AROOT%40ODL.MIT.EDU')
BOOTSTRAP_VAULT_TYPE = Type(authority='ODL.MIT.EDU', namespace='authorization.Vault', identifier='bootstrap_vault')
OVERRIDE_VAULT_TYPE = Type(authority='ODL.MIT.EDU', namespace='authorization.Vault', identifier='override_vault')
DEFAULT_TYPE = Type(**{'identifier': 'DEFAULT', 'namespace': 'DEFAULT', 'authority': 'DEFAULT'})
DEFAULT_GENUS_TYPE = Type(**{'identifier': 'DEFAULT', 'namespace': 'GenusType', 'authority': 'DLKIT.MIT.EDU'})
ALIAS_ID = Id(**{'identifier': 'ALIAS', 'namespace': 'ALIAS', 'authority': 'ALIAS'})
AGENT_ID = Id(**{'identifier': 'jane_doe', 'namespace': 'osid.agent.Agent', 'authority': 'MIT-ODL'})
NEW_TYPE = Type(**{'identifier': 'NEW', 'namespace': 'MINE', 'authority': 'YOURS'})
NEW_TYPE_2 = Type(**{'identifier': 'NEW 2', 'namespace': 'MINE', 'authority': 'YOURS'})
BLUE_TYPE = Type(authority='BLUE', namespace='BLUE', identifier='BLUE')


@pytest.fixture(scope="class",
                params=['TEST_SERVICE'])
def authz_adapter_class_fixture(request):
    request.cls.service_config = request.param
    request.cls.authz_mgr = Runtime().get_manager(
        'AUTHORIZATION',
        implementation='TEST_SERVICE')
    if not is_never_authz(request.cls.service_config):
        request.cls.vault_admin_session = request.cls.authz_mgr.get_vault_admin_session()
        request.cls.vault_lookup_session = request.cls.authz_mgr.get_vault_lookup_session()

        create_form = request.cls.vault_admin_session.get_vault_form_for_create([])
        create_form.display_name = 'Test Vault'
        create_form.description = 'Test Vault for AuthorizationSession tests'
        create_form.genus_type = BOOTSTRAP_VAULT_TYPE
        request.cls.vault = request.cls.vault_admin_session.create_vault(create_form)

        create_form = request.cls.vault_admin_session.get_vault_form_for_create([])
        create_form.display_name = 'Test Override Vault'
        create_form.description = 'Test Override Vault for AuthorizationSession tests'
        create_form.genus_type = OVERRIDE_VAULT_TYPE
        request.cls.override_vault = request.cls.vault_admin_session.create_vault(create_form)

        request.cls.authz_admin_session = request.cls.authz_mgr.get_authorization_admin_session_for_vault(request.cls.vault.ident)
        request.cls.override_authz_admin_session = request.cls.authz_mgr.get_authorization_admin_session_for_vault(request.cls.override_vault.ident)
        request.cls.authz_lookup_session = request.cls.authz_mgr.get_authorization_lookup_session_for_vault(request.cls.vault.ident)

        request.cls.gradebook_list = list()
        request.cls.gradebook_id_list = list()
        request.cls.authz_list = list()
        request.cls.authz_id_list = list()
        request.cls.grading_mgr = Runtime().get_service_manager(
            'GRADING',
            proxy=PROXY,
            implementation='TEST_SERVICE')
        for num in [0, 1, 2, 3, 4, 5, 6, 7]:
            create_form = request.cls.grading_mgr.get_gradebook_form_for_create([])
            create_form.display_name = 'Test Gradebook ' + str(num)
            create_form.description = 'Test Gradebook for Testing Authorization Number: ' + str(num)
            gradebook = request.cls.grading_mgr.create_gradebook(create_form)
            request.cls.gradebook_list.append(gradebook)
            request.cls.gradebook_id_list.append(gradebook.ident)

        request.cls.grading_mgr.add_root_gradebook(request.cls.gradebook_id_list[0])
        request.cls.grading_mgr.add_child_gradebook(request.cls.gradebook_id_list[0], request.cls.gradebook_id_list[1])
        request.cls.grading_mgr.add_child_gradebook(request.cls.gradebook_id_list[0], request.cls.gradebook_id_list[2])
        request.cls.grading_mgr.add_child_gradebook(request.cls.gradebook_id_list[1], request.cls.gradebook_id_list[3])
        request.cls.grading_mgr.add_child_gradebook(request.cls.gradebook_id_list[1], request.cls.gradebook_id_list[4])
        request.cls.grading_mgr.add_child_gradebook(request.cls.gradebook_id_list[2], request.cls.gradebook_id_list[5])

        # The hierarchy should look like this. (t) indicates where lookup is
        # explicitely authorized:
        #
        #            _____ 0 _____
        #           |             |
        #        _ 1(t) _         2     not in hierarchy
        #       |        |        |
        #       3        4       5(t)      6     7(t)   (the 'blue' gradebook_column in gradebook 2 is also assigned to gradebook 7)

        request.cls.svc_mgr = Runtime().get_service_manager(
            'AUTHORIZATION',
            proxy=PROXY,
            implementation=request.cls.service_config)
        request.cls.catalog = request.cls.svc_mgr.get_vault(request.cls.vault.ident)

        # Set up Gradebook lookup authorization for Jane
        create_form = request.cls.authz_admin_session.get_authorization_form_for_create_for_agent(
            AGENT_ID,
            LOOKUP_GRADEBOOK_FUNCTION_ID,
            ROOT_QUALIFIER_ID,
            [])
        create_form.display_name = 'Jane Lookup Authorization'
        create_form.description = 'Test Authorization for AuthorizationSession tests'
        jane_lookup_authz = request.cls.authz_admin_session.create_authorization(create_form)
        request.cls.authz_list.append(jane_lookup_authz)
        request.cls.authz_id_list.append(jane_lookup_authz.ident)

        # Set up GradebookColumn lookup authorizations for Jane
        for num in [1, 5]:
            create_form = request.cls.authz_admin_session.get_authorization_form_for_create_for_agent(
                AGENT_ID,
                LOOKUP_GRADEBOOK_COLUMN_FUNCTION_ID,
                request.cls.gradebook_id_list[num],
                [])
            create_form.display_name = 'Test Authorization ' + str(num)
            create_form.description = 'Test Authorization for AuthorizationSession tests'
            authz = request.cls.authz_admin_session.create_authorization(create_form)
            request.cls.authz_list.append(authz)
            request.cls.authz_id_list.append(authz.ident)

        # Set up GradebookColumn lookup override authorizations for Jane
        for num in [7]:
            create_form = request.cls.override_authz_admin_session.get_authorization_form_for_create_for_agent(
                AGENT_ID,
                LOOKUP_GRADEBOOK_COLUMN_FUNCTION_ID,
                request.cls.gradebook_id_list[num],
                [])
            create_form.display_name = 'Test Authorization ' + str(num) + ' (override)'
            create_form.description = 'Test Authorization for AuthorizationSession tests'
            authz = request.cls.override_authz_admin_session.create_authorization(create_form)
            request.cls.authz_list.append(authz)
            request.cls.authz_id_list.append(authz.ident)

        # Set up GradebookColumn search override authorizations for Jane
        for num in [7]:
            create_form = request.cls.override_authz_admin_session.get_authorization_form_for_create_for_agent(
                AGENT_ID,
                SEARCH_GRADEBOOK_COLUMN_FUNCTION_ID,
                request.cls.gradebook_id_list[num],
                [])
            create_form.display_name = 'Test Authorization ' + str(num) + ' (override)'
            create_form.description = 'Test Authorization for AuthorizationSession tests'
            authz = request.cls.override_authz_admin_session.create_authorization(create_form)
            request.cls.authz_list.append(authz)
            request.cls.authz_id_list.append(authz.ident)

        # Set up GradebookColumn search authorizations for Jane
        for num in [1, 5]:
            create_form = request.cls.authz_admin_session.get_authorization_form_for_create_for_agent(
                AGENT_ID,
                SEARCH_GRADEBOOK_COLUMN_FUNCTION_ID,
                request.cls.gradebook_id_list[num],
                [])
            create_form.display_name = 'Test Authorization ' + str(num)
            create_form.description = 'Test Authorization for AuthorizationSession tests'
            authz = request.cls.authz_admin_session.create_authorization(create_form)
            request.cls.authz_list.append(authz)
            request.cls.authz_id_list.append(authz.ident)

    else:
        request.cls.catalog = request.cls.svc_mgr.get_authorization_session(proxy=PROXY)

    def class_tear_down():
        if not is_never_authz(request.cls.service_config):
            for catalog in request.cls.grading_mgr.get_gradebooks():
                for obj in catalog.get_gradebook_columns():
                    catalog.delete_gradebook_column(obj.ident)
                request.cls.grading_mgr.delete_gradebook(catalog.ident)
            for vault in request.cls.vault_lookup_session.get_vaults():
                lookup_session = request.cls.authz_mgr.get_authorization_lookup_session_for_vault(vault.ident)
                admin_session = request.cls.authz_mgr.get_authorization_admin_session_for_vault(vault.ident)
                for authz in lookup_session.get_authorizations():
                    admin_session.delete_authorization(authz.ident)
                request.cls.vault_admin_session.delete_vault(vault.ident)

    request.addfinalizer(class_tear_down)


@pytest.fixture(scope="function")
def authz_adapter_test_fixture(request):
    request.cls.gradebook_column_id_lists = []
    count = 0
    if not is_never_authz(request.cls.service_config):
        for gradebook_ in request.cls.gradebook_list:
            request.cls.gradebook_column_id_lists.append([])
            for color in ['Red', 'Blue', 'Red']:
                create_form = gradebook_.get_gradebook_column_form_for_create([])
                create_form.display_name = color + ' ' + str(count) + ' GradebookColumn'
                create_form.description = color + ' gradebook_column for authz adapter tests from Gradebook number ' + str(count)
                if color == 'Blue':
                    create_form.genus_type = BLUE_TYPE
                gradebook_column = gradebook_.create_gradebook_column(create_form)
                if count == 2 and color == 'Blue':
                    request.cls.grading_mgr.assign_gradebook_column_to_gradebook(
                        gradebook_column.ident,
                        request.cls.gradebook_id_list[7])
                request.cls.gradebook_column_id_lists[count].append(gradebook_column.ident)
            count += 1

    def test_tear_down():
        if not is_never_authz(request.cls.service_config):
            for index, gradebook_ in enumerate(request.cls.gradebook_list):
                for gradebook_column_id in request.cls.gradebook_column_id_lists[index]:
                    gradebook_.delete_gradebook_column(gradebook_column_id)

    request.addfinalizer(test_tear_down)


@pytest.mark.usefixtures("authz_adapter_class_fixture", "authz_adapter_test_fixture")
class TestGradebookColumnAuthzAdapter(object):

    def test_lookup_gradebook_0_plenary_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            # with pytest.raises(errors.NotFound):
            #     gradebook_columns = gradebook.get_gradebook_columns()
            # with pytest.raises(errors.NotFound):
            #     gradebook_columns = gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE)
            # for gradebook_column_id in self.gradebook_column_id_lists[0]:
            #     with pytest.raises(errors.NotFound):
            #         gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)
            # with pytest.raises(errors.NotFound):
            #     gradebook_columns = gradebook.get_gradebook_columns_by_ids(self.gradebook_column_id_lists[0])

    def test_lookup_gradebook_0_plenary_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_federated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.can_lookup_gradebook_columns()
            assert gradebook.get_gradebook_columns().available() == 1
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).next().ident == self.gradebook_column_id_lists[2][1]
            gradebook.get_gradebook_column(self.gradebook_column_id_lists[2][1])
            for gradebook_column_num in [0, 2]:
                with pytest.raises(errors.NotFound):  # Is this right?  Perhaps PermissionDenied
                    gradebook_column = gradebook.get_gradebook_column(self.gradebook_column_id_lists[2][gradebook_column_num])

    def test_lookup_gradebook_0_comparative_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_federated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            # print "START"
            assert gradebook.get_gradebook_columns().available() == 13
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 5
            for gradebook_column in gradebook.get_gradebook_columns():
                gradebook.get_gradebook_column(gradebook_column.ident)
            gradebook_column_ids = [gradebook_column.ident for gradebook_column in gradebook.get_gradebook_columns()]
            gradebook.get_gradebook_columns_by_ids(gradebook_column_ids)
            for gradebook_column_id in self.gradebook_column_id_lists[0]:
                with pytest.raises(errors.NotFound):
                    gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)
            gradebook_column = gradebook.get_gradebook_column(self.gradebook_column_id_lists[2][1])
            for gradebook_column_num in [0, 2]:
                with pytest.raises(errors.NotFound):
                    gradebook_column = gradebook.get_gradebook_column(self.gradebook_column_id_lists[2][gradebook_column_num])
            for gradebook_column_id in self.gradebook_column_id_lists[1]:
                    gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)
            for gradebook_column_id in self.gradebook_column_id_lists[3]:
                    gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)
            for gradebook_column_id in self.gradebook_column_id_lists[4]:
                    gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)
            for gradebook_column_id in self.gradebook_column_id_lists[5]:
                    gradebook_column = gradebook.get_gradebook_column(gradebook_column_id)

    def test_lookup_gradebook_0_comparative_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 0
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 0

    def test_lookup_gradebook_1_plenary_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_lookup_gradebook_1_plenary_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_federated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 9
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 3

    def test_lookup_gradebook_1_comparative_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_federated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 9
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 3

    def test_lookup_gradebook_1_comparative_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_lookup_gradebook_2_plenary_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[2])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 1
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns()
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE)

    def test_lookup_gradebook_2_plenary_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[2])
            gradebook.use_federated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 1
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns()
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE)

    def test_lookup_gradebook_2_comparative_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[2])
            gradebook.use_federated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 4
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 2
            # self.assertEqual(gradebook.get_gradebook_columns().available(), 3)
            # self.assertEqual(gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available(), 1)

    def test_lookup_gradebook_2_comparative_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[2])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 1
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns()
            # with pytest.raises(errors.PermissionDenied):
            #     gradebook_columns = gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE)

    def test_lookup_gradebook_3_plenary_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[3])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_lookup_gradebook_3_plenary_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[3])
            gradebook.use_federated_gradebook_view()
            gradebook.use_plenary_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_lookup_gradebook_3_comparative_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[3])
            gradebook.use_federated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_lookup_gradebook_3_comparative_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[3])
            gradebook.use_isolated_gradebook_view()
            gradebook.use_comparative_gradebook_column_view()
            assert gradebook.get_gradebook_columns().available() == 3
            assert gradebook.get_gradebook_columns_by_genus_type(BLUE_TYPE).available() == 1

    def test_query_gradebook_0_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_isolated_gradebook_view()
            with pytest.raises(errors.PermissionDenied):
                query = gradebook.get_gradebook_column_query()

    def test_query_gradebook_0_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[0])
            gradebook.use_federated_gradebook_view()
            query = gradebook.get_gradebook_column_query()
            query.match_display_name('red')
            assert gradebook.get_gradebook_columns_by_query(query).available() == 8
            query.clear_display_name_terms()
            query.match_display_name('blue')
            assert gradebook.get_gradebook_columns_by_query(query).available() == 5

    def test_query_gradebook_1_isolated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_isolated_gradebook_view()
            query = gradebook.get_gradebook_column_query()
            query.match_display_name('red')
            assert gradebook.get_gradebook_columns_by_query(query).available() == 2

    def test_query_gradebook_1_federated(self):
        if not is_never_authz(self.service_config):
            janes_grading_mgr = Runtime().get_service_manager(
                'GRADING',
                proxy=JANE_PROXY,
                implementation='TEST_SERVICE_JSON_AUTHZ')
            gradebook = janes_grading_mgr.get_gradebook(self.gradebook_id_list[1])
            gradebook.use_federated_gradebook_view()
            query = gradebook.get_gradebook_column_query()
            query.match_display_name('red')
            assert gradebook.get_gradebook_columns_by_query(query).available() == 6
