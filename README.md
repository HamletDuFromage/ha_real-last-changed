# Real last changed

<a href="https://liberapay.com/HamletDuFromage/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>
[![btc](https://img.shields.io/badge/BTC-1CoFc1bY5AHLP6Noe1zmqnJnp7ZWBxyo79-yellow?logo=bitcoin)](https://github.com/HamletDuFromage/aio-switch-updater#like-the-app)
[![eth](https://img.shields.io/badge/ETH-0xf68f568e21a15934e0e9a6949288c3ca009140ba-purple?logo=ethereum)](https://github.com/HamletDuFromage/aio-switch-updater#like-the-app)
[![xmr](https://img.shields.io/badge/XMR-88wjCuhHX3oNhVpEdYeUx3LvrkdTvcTHx7v7L5fQpjCg7QiAReJUVR4LPase5Byj2UhdVdLtvysJaXTFKq2EnuvuLjvQMGL-orange?logo=monero)](https://github.com/HamletDuFromage/aio-switch-updater#like-the-app)

[![hacs][hacsbadge]][hacs]

This component creates entities that track the last time an entity's state has actually been changed. This is meant to make `last_changed` useful even after a HA restart. 

There have been multiple feature requests over the years to make the last changed state persist reboots. 
[2019](https://community.home-assistant.io/t/retain-last-state-change-data-of-a-sensor-after-reboot/125148) [2020](https://community.home-assistant.io/t/what-the-heck-is-with-the-latest-state-change-not-being-kept-after-restart/219480) [2022](https://community.home-assistant.io/t/persistent-version-of-last-changed-for-the-ui/467163) [2024](https://community.home-assistant.io/t/wth-there-is-no-new-last-attribute-that-retains-restart/802413)

![icon][iconimg]

## Installation
### Using [HACS](https://hacs.xyz/) 
1. Go to HACS section;
2. From the 3 dots menu (top right) click on **Add custom repository**;
3. Add as **Integration** this url https://github.com/HamletDuFromage/ha_real-last-changed;
4. Search and install **Restore Persistent Notification** from the HACS integration list;
5. Add this integration from the **Home Assistant** integrations.

### Manually
1. Download this repository;
2. Copy the directory **custom_components/ha_real-last-changed** on your Home Assistant **config/custom_components/ha_real-last-changed**;
3. Restart HomeAssistant;
4. Add this integration from the **Home Assistant** integrations.

<img src="https://github.com/user-attachments/assets/37360351-8927-41ce-b52d-a7b14b2108fd" />

<!---->


---

[ha_real-last-changed]: https://github.com/custom-components/ha_real-last-changed
[commits-shield]: https://img.shields.io/github/commit-activity/y/HamletDuFromage/ha_real-last-changed.svg?style=for-the-badge
[commits]: https://github.com/HamletDuFromage/ha_real-last-changed/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[iconimg]: icon.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/HamletDuFromage/ha_real-last-changed.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40HamletDuFromage-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/HamletDuFromage/ha_real-last-changed.svg?style=for-the-badge
[releases]: https://github.com/HamletDuFromage/ha_real-last-changed/releases
[user_profile]: https://github.com/HamletDuFromage
