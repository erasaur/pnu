#!/usr/bin/env python3.5
import unittest

from pnu.apis.poke_api import PnuPokeApi
from pnu.tests.mock import PnuPokeApiMock
from pnu.models.user import User


class PnuPokeApiTests(unittest.TestCase):

    def test_all(self):
        poke_api = PnuPokeApiMock()

        sterling_loc = (42.280601, -83.743595)
        firestone_loc = (42.280889, -83.743722)
        varsity_loc = (42.280577, -83.742928)
        arbor_loc = (42.280844, -83.744341)

        sterling = User({
            "latitude": sterling_loc[0],
            "longitude": sterling_loc[1],
        })
        firestone = User({
            "latitude": firestone_loc[0],
            "longitude": firestone_loc[1],
        })
        varsity = User({
            "latitude": varsity_loc[0],
            "longitude": varsity_loc[1],
        })
        arbor = User({
            "latitude": arbor_loc[0],
            "longitude": arbor_loc[1],
        })

        poke_api.update_data(sterling, False)
        poke_api.update_data(firestone, False)
        poke_api.update_data(varsity, False)

        # sterling, firestone, and varsity should form a clique
        assert poke_api.close_enough(sterling, sterling)
        assert poke_api.close_enough(sterling, firestone)
        assert poke_api.close_enough(sterling, varsity)
        assert poke_api.close_enough(firestone, varsity)
        assert len(poke_api._groups) == 1 # should be only 1 group so far

        # arbor should be close enough to sterling and firestone, but not to varsity
        poke_api.update_data(arbor, False)
        assert poke_api.close_enough(arbor, sterling)
        assert poke_api.close_enough(arbor, firestone)
        assert not poke_api.close_enough(arbor, varsity)

        # so arbor shouldn't be in the clique, we should have a new group
        assert len(poke_api._groups) == 2

        assert not poke_api.pos_changed(sterling, sterling)
        assert poke_api.pos_changed(sterling, firestone)

        # center of group should be close enough to everyone in the group
        group_0 = poke_api._groups[0]
        group_0_loc = poke_api.get_cover(group_0)
        group_0_proxy = User({
            "latitude": group_0_loc[0],
            "longitude": group_0_loc[1]
        })
        for member in group_0:
            assert poke_api.close_enough(group_0_proxy, member)


if __name__ == "__main__":
    unittest.main()
