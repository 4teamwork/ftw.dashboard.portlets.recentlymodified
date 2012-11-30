from ftw.upgrade import UpgradeStep


class UpdateActionsDescription(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.dashboard.portlets.recentlymodified.upgrades:1270')