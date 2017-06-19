# Change log


## v 0.0.9 - May. 29, 2017

*Implement group module*

**Add**

`Group Management`
- rest_gm_add.py
- rest_gm_add_device.py
- rest_gm_delete.py
- rest_gm_delete_device.py
- rest_gm_update.py

**Update**
- CHANGELOG.md
- README.md

**Remove**

`none`

## v 0.0.8 - May. 29, 2017

*Add Module E-Savor*

**Add**

`E Savor`
- rest_esavor_clear_filter.py
- rest_esavor_toggle_filter.py

**Update**
- CHANGELOG.md
- README.md

**Remove**

`none`

## v 0.0.7 - May. 29, 2017

*Add new function in Device Management Module*

**Add**

`Device Management`
- rest_dm_edit_device.py
- rest_dm_get_device_by_mac.py
- rest_dm_get_time_line.py
- rest_dm_perform_action.py
- rest_dm_un_register_device.py


**Update**
- CHANGELOG.md
- README.md

**Remove**

`none`

## v 0.0.6 - May. 26, 2017

*Implement stats module*

**Add**

`Stats Management`
- rest_stm_by_zone.py

`Module Abstract Classes`
- stats_management.py
- stats_management_day.py
- stats_management_hour.py
- stats_management_week.py

`Module Classes`
- device_metering_data_cost_day.py
- device_metering_data_cost_hour.py
- device_metering_data_cost_week.py
- device_stats_duration_day.py
- device_stats_duration_hour.py
- device_stats_duration_week.py
- device_stats_temperature_day.py
- device_stats_temperature_week.py
- device_stats_temperature_hour.py

`Module helper Classes`
- custom_date.py
- time_zone.py       


**Update**
- CHANGELOG.md
- README.md

**Remove**
- schedule_management.py

## v 0.0.5 -  May. 17, 2017

*Implement new module, add new models, update imports*

**Add**

`Schedular-Management`
- rest_sm_add_schedule.py
- rest_sm_delete_schedule.py
- rest_sm_edit_schedule.py
- rest_sm_get_schedule_lists.py
- rest_sm_set_is_enabled.py

`Model`
- schedule_notifications.py
- scheduler.py

`Module Abstract Classes`
- schedule_management.py

**Update**
- CHANGELOG.md
- README.md
- table.py

**Remove**

`none`

## v 0.0.4 -  May. 16, 2017

*Implement new module, add new models, update imports,*

**Add**

`Device-Management`
- rest_dm_change_appliance.py
- rest_dm_e_saver_modes_settings.py
- rest_dm_get_devices.py
- rest_dm_register_device.py
- rest_dm_set_intelli_mode.py
- rest_dm_setIs_weather_enabled.py
- rest_dm_update_device_location_threshold.py
- rest_dm_update_device_settings.py

`Model`
- devices.py
- things.py
- group.py
- authentic_devices.py
- actions.py

**Update**
- CHANGELOG.md
- README.md

**Remove**

`none`

## v 0.0.3 -  May. 10, 2017

*Implement new module, add new models, update imports,*

**Add**

`User-Management`
- rest_um_validate_token.py
- rest_um_social_login.py
- rest_um_change_password.py
- rest_um_edit_user_profile.py
- rest_um_forget_password.py
- rest_um_get_child_users.py
- rest_um_get_notification_settings.py
- rest_um_get_user_image.py
- rest_um_get_user_profile.py
- rest_um_register_installation.py
- rest_um_send_user_feedback.py
- rest_um_set_currency_and_pricing.py
- rest_um_set_notification_settings.py
- rest_um_signin.py
- rest_um_signout.py
- rest_um_signup.py

`Configuration`
- rest_config_get_version.py
- rest_config_sync_appliances_manufacturers.py
- rest_config_sync_db.py

`JWT token validator`
- rest_auth.py

`Util`
- util.py

`Model`
- appliance.py
- appliance_codes.py
- appliance_rules.py
- central_system.py
- device_state.py
- feedback.py
- installations.py
- manufacturer.py
- user.py

`Git Configurations`
- .gitignore

**Update**

`Classes`
- constant.py
- custom_jtw.py
- response.py
- table.py
- user_role.py (renamed to user_level.py)

**Remove**

`none`


## v 0.0.2 - Apr. 06, 2017

*Create Base Architecture*

**Add**

`Classes`
- constant.py
- custom_jtw.py
- response.py
- table.py
- user_role.py


`libraries`
- JTW
- pythonLangUtil

**Update**
- CHANGELOG.md
- README.md

**Remove**

`none`


## v 0.0.1 - Apr. 06, 2017

*Initial Release.*

**Implementation:**

- README.md
- CHANGELOG.md
