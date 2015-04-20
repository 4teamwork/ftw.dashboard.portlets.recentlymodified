from ftw.upgrade import UpgradeStep


class AddRegistryRecord(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.dashboard.portlets.recentlymodified.upgrades:1281')
