import unittest
from csc440user import UserManager

class UserContentTestCase(unittest):
    """
        Various test cases around user content.
    """
    def test_get_user(self):
        """
            Assert that users are retrieved and data is correct
        """
        manager = UserManager("hash", "tests")

        user = manager.get_user("testUser1")
        assert user is not None
        assert user.name == "testUser1"
        assert user.get("password") == "password1"
        assert user.get("roles") == []

        user2 = manager.get_user("testUser2")
        assert user2 is not None
        assert user2.name == "testUser2"
        assert user2.get("password") == "password2"
        assert user2.get("roles") == ["testRole1", "testRole2"]


    def test_add_update_delete_user(self):
        """
             Ensure users are added to the database correctly
        """

        manager = UserManager("hash", "tests")

        #Add Users
        manager.add_user("testUserAdd", "password", True, [], "cleartext")
        manager.add_user("testUserAddWithRoles", "password2", True, ["testAddRole1", "testAddRole2"], "cleartext")

        user = manager.get_user("testUserAdd")
        assert user is not None
        assert user.name == "testUserAdd"
        assert user.get("password") == "password"
        assert user.get("roles") == []

        user2 = manager.get_user("testUserAddWithRoles")
        assert user2 is not None
        assert user2.name == "testUserAddWithRoles"
        assert user2.get("password") == "password2"
        assert user2.get("roles") == ["testAddRole1", "testAddRole2"]


        #Update Users

        userdata = {}
        userdata["password"] = "password"
        userdata["authenticated"] = 0
        userdata["active"] = 1
        userdata["authentication_method"] = "cleartext"
        userdata["roles"] = ["testRoleUpdate"]

        manager.update("testUserAdd", userdata)

        user = manager.get_user("testUserAdd")
        assert user is not None
        assert user.name == "testUserAdd"
        assert user.get("password") == "password"
        assert user.get("roles") == ["testRoleUpdate"]

        #Delete Users
        manager.delete_user("testUserAdd")
        manager.delete_user("testUserAddWithRoles")

        user = manager.get_user("testUserAdd")
        user2 = manager.get_user("testUserAddWithRoles")

        assert user is None
        assert user2 is None
