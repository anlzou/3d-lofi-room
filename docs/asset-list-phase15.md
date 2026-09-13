# Phase 1.5 最终布局资产清单

本清单按当前已摆放灰模定稿。Phase 1.5 已建立位置与占位；Phase 2 精修造型材质；Phase 3 UV/烘焙；Phase 4 实现动画交互。灰模中季节物件同时显示以便检查占地，运行时功能尚未开启。

| 编号 | 资产组 | 优先级 | 布局 | 精修 | 动效/交互 |
| --- | --- | --- | --- | --- | --- |
| 01 | CRT + tilted cabinet | P0 | 1.5 完成 | 2 | 4 |
| 02 | VHS recorder / door | P0 | 1.5 完成 | 2 | 4 |
| 03 | DVD player / tray | P0 | 1.5 完成 | 2 | 4 |
| 04 | VHS labels / DVD cases | P1 | 1.5 完成 | 2 | 4 |
| 05 | Console / controller / cable / remote | P1 | 1.5 完成 | 2 | 4 |
| 06 | Desk 0.72m / Mac 0.34m | P0 | 1.5 完成 | 2 | 4 |
| 07 | Keyboard / mouse | P0 | 1.5 完成 | 2 | 4 |
| 08 | Task lamp | P1 | 1.5 完成 | 2 | 4 |
| 09 | Computer tower | P1 | 1.5 完成 | 2 | 4 |
| 10 | Modem / coiled phone cable | P1 | 1.5 完成 | 2 | 4 |
| 11 | Pair of speakers | P1 | 1.5 完成 | 2 | 4 |
| 12 | Flip clock / calendar | P1 | 1.5 完成 | 2 | 4 |
| 13 | Noodles / mug / stationery | P1 | 1.5 完成 | 2 | 4 |
| 14 | Walkman / headphones / cable | P1 | 1.5 完成 | 2 | 4 |
| 15 | Floppy box / loose CDs | P1 | 1.5 完成 | 2 | 4 |
| 16 | Power strip / six device cables / plugs | P1 | 1.5 完成 | 2 | 4 |
| 17 | Long wall shelf / CD tower / globe / figures / Lego / manuals | P1 | 1.5 完成 | 2 | 4 |
| 18 | Three skewed posters | P1 | 1.5 完成 | 2 | 4 |
| 19 | Corkboard / photos / notes / tickets | P1 | 1.5 完成 | 2 | 4 |
| 20 | Wall clock / hands | P1 | 1.5 完成 | 2 | 4 |
| 21 | Low bookshelf / skateboard | P1 | 1.5 完成 | 2 | 4 |
| 22 | Raised bed / folded duvet / cushion / open comic | P1 | 1.5 完成 | 2 | 4 |
| 23 | Nightstand / alarm / water / nightlight | P1 | 1.5 完成 | 2 | 4 |
| 24 | Pair of slippers | P1 | 1.5 完成 | 2 | 4 |
| 25 | Cat bed / sleeping cat | P1 | 1.5 完成 | 2 | 4 |
| 26 | Bin / missed paper balls | P1 | 1.5 完成 | 2 | 4 |
| 27 | Scattered magazines | P1 | 1.5 完成 | 2 | 4 |
| 28 | Foreground plant / record crate | P1 | 1.5 完成 | 2 | 4 |
| 29 | Sill plant / tiny bird figure | P1 | 1.5 完成 | 2 | 4 |
| 30 | Movable blinds / weather sockets / chime | P1 | 1.5 完成 | 2 | 4 |
| 31 | Fan / heater / kettle / spring flowers / throw / scarf / iced drink | P1 | 1.5 完成 | 2 | 4 |
| 32 | Four cat destinations | P1 | 1.5 完成 | 2 | 4 |
| 33 | Ceiling / pullcord / string path / lava lamp / five anchors | P1 | 1.5 完成 | 2 | 4 |
| 34 | Utility pole / wires / houses / fence | P1 | 1.5 完成 | 2 | 4 |
| 35 | Underbed boxes / frayed rug edge | P1 | 1.5 完成 | 2 | 4 |

## 明确取舍

- 选落地植物，未增鱼缸；选滑板，未增吉他；选熔岩灯，未增霓虹牌；选泡面碗，未增零食袋，均为本轮提示词允许的二选一。
- 海报、照片、票根与便签先共用灰色纸片语言，图案和文字在 Phase 2 精修；没有因此删除位置。
- 暖炉是电热器灰模，冬季猫窝使用 SOCKET_cat_heater；所有灯具位置已摆放，夜景只开启台灯和屏幕。
- 补充了唱片收纳箱、床下收纳盒、地毯翘边，强化使用痕迹。
- 未将原始模型合并或删掉。网页仅将不可交互的静态网格按材质临时合批，GLB 保留名称和挂点。

## 精确对象名索引

下表逐项覆盖源场景全部对象（包括不可见挂点、预览灯光与相机）。P0 为房间/英雄设备/窗外主要骨架，其余为 P1；灯光相机仅预览，不随 GLB 导出。

| 对象名 | 优先级 | 当前阶段 | 下一阶段 | 类型 |
| --- | --- | --- | --- | --- |
| `ANIM_blinds_slat_00` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_blinds_slat_01` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_blinds_slat_02` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_blinds_slat_03` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_blinds_slat_04` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_clock_hour` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_clock_minute` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_dvd_tray` | P0 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_fan_blade_00` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_fan_blade_01` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_fan_blade_02` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `ANIM_fan_head` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `ANIM_vcr_door` | P0 | 1.5 已摆放 | 4 接入 | MESH |
| `Alarm_Body` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Blanket` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Cushion` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Frame` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Headboard` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Mattress` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Bed_Pillow` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Foreground` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Record_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Record_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Record_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Record_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Box_Record_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Device_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_GameController` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Headphone` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Mains` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cable_Phone_Coil` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Camera_Desk` | P1 | 1.5 已摆放 | 预览配置，不导出 | CAMERA |
| `Camera_Plan` | P1 | 1.5 已摆放 | 预览配置，不导出 | CAMERA |
| `Camera_Room` | P1 | 1.5 已摆放 | 预览配置，不导出 | CAMERA |
| `Camera_Window` | P1 | 1.5 已摆放 | 预览配置，不导出 | CAMERA |
| `Cat_Bed` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cat_Ear` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cat_Ear.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cat_Head` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cat_Placeholder` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cat_Tail` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cd_Loose_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Cd_Loose_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Ceiling_PullWeight` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Ceiling_Shade` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Ceiling_Suspension` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Back` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Leg` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Leg.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Leg.002` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Leg.003` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Chair_Seat` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Comic_OpenLeft` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Comic_OpenRight` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Comic_Panel_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Comic_Panel_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Comic_Panel_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Computer_Drive` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Computer_Tower` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Photo_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Corkboard_Pin_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Crt_AntennaLeft` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Crt_AntennaRight` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Crt_Bezel` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Crt_Body` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Crt_ScreenBacking` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Desk_Leg` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Desk_Leg.001` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Desk_Leg.002` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Desk_Leg.003` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Desk_Main` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Dvd_Body` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Dvd_Case_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Dvd_Case_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Dvd_Case_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Dvd_Case_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_led_modem_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_led_modem_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_led_modem_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_led_modem_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_screen_alarm` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_screen_crt` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_screen_flip` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `EMIT_screen_mac` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Crossarm` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_FenceRail` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_FenceRail.001` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_05` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_06` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_07` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_08` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_09` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_10` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_11` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_12` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_13` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_14` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Fence_15` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_House_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_House_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_House_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Powerline_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Powerline_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Roof_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Roof_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Roof_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_UtilityPole` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_00_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_00_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_01_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_01_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_02_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Exterior_Window_02_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Fan_Base` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Fan_Guard` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Fan_Stem` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Figurine_Body_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Figurine_Body_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Figurine_Head_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Figurine_Head_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_05` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_06` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_07` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_08` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_09` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_10` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_11` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_12` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_13` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_14` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_15` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_16` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floor_Plank_17` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floppy_Box` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floppy_Disk_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floppy_Disk_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floppy_Disk_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Floppy_Disk_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `GameConsole_Body` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Game_Controller` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Game_ControllerGrip` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Game_ControllerGrip.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Globe_Sphere` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Globe_Stand` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Headphones_Band` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Headphones_Earcup` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Headphones_Earcup.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Heater_Grille_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Heater_Grille_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Heater_Grille_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Heater_Grille_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Heater_Grille_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `INT_calendar` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_cat` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_ceiling_pullcord` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_clock_flip` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_clock_wall` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_dvd` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_lamp_desk` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_lava_lamp` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_mac` | P0 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_phone` | P1 | 1.5 已摆放 | 4 接入 | MESH |
| `INT_tv_crt` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_vcr` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `INT_window` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `Kettle_Body` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Kettle_Handle` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Kettle_Spout` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Base` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_05` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_06` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_07` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_08` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_00_09` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_05` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_06` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_07` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_08` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_01_09` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_05` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_06` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_07` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_08` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Keyboard_Key_02_09` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LIGHT_ceiling` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `LIGHT_desk_lamp` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `LIGHT_heater` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `LIGHT_lava_lamp` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `LIGHT_string_lights` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `Lamp_Base` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lamp_LowerArm` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lamp_Shade` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lamp_UpperArm` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lamp_Warm` | P1 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `LavaLamp_Base` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lego_Block_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lego_Block_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lego_Block_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Lego_Block_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_06` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_00_07` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_06` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Book_01_07` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `LowBookshelf_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mac_Body` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mac_DriveSlot` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mac_Foot` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mac_ScreenBacking` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mac_ScreenInset` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Magazine_Floor_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Magazine_Floor_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Magazine_Floor_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Magazine_Floor_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Manual_Shelf_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Manual_Shelf_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Manual_Shelf_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Modem_Body` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mouse_Main` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Mug_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Nightlight_Shade` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Nightlight_Stem` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Nightstand_Drawer` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Nightstand_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Nightstand_Water` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Noodles_Bowl` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Noodles_ChopstickA` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Noodles_ChopstickB` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Notebook_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Paper_Crumpled_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Paper_Crumpled_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Paper_Crumpled_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Pencil_Cup` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Phone_Receiver` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Leaf_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Pot` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Foreground_Stem_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf.002` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf.003` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf.004` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Leaf.005` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Pot` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem.002` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem.003` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem.004` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Stem.005` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Leaf_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Pot` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Plant_Windowsill_Stem_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Caption_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Caption_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Caption_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Moon_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Moon_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Poster_Moon_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `PowerStrip_Plug_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Room_Fill` | P0 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `Room_Foundation` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Rug_FrayedEdge` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Rug_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `SEASON_autumn_blanket` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `SEASON_spring_flowerpot` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SEASON_summer_fan` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SEASON_summer_iceddrink` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `SEASON_winter_heater` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `SEASON_winter_scarf` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `SOCKET_cat_bed` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_cat_fan` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_cat_heater` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_cat_windowsill` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_kettle_steam` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_petals_window` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_rain_window` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_steam_mug` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `SOCKET_windchime` | P1 | 1.5 已摆放 | 4 接入 | EMPTY |
| `ScreenBounce_Crt` | P1 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `ScreenBounce_Mac` | P1 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `Shelf_Book_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Book_06` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Shelf_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Skateboard_Axle` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Skateboard_Axle.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Skateboard_Deck` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Skirting_Back` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Skirting_Right` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Slipper_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Slipper_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Speaker_0` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Speaker_1` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Speaker_Cone_0` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Speaker_Cone_1` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Blossom` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Blossom.001` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Leaf_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Pot` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Spring_Flowers_Stem_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Desk_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Desk_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Desk_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Desk_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Mac_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sticky_Mac_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_06` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_07` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_08` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_09` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_10` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_11` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_12` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Bulb_13` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `StringLights_Wire` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Sun_Evening` | P1 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `Tree_Branch_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Branch_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Branch_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Branch_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Branch_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Canopy_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Canopy_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Canopy_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Canopy_03` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Canopy_04` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tree_Trunk` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `TvStand_Main` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `TvStand_Shelf` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Tv_Remote` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `UnderBed_Storage_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `UnderBed_Storage_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `UnderBed_Storage_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_Body` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_ExtraTape_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_ExtraTape_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_ExtraTape_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_ExtraTape_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_ExtraTape_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_HandLabel_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_HandLabel_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_HandLabel_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_HandLabel_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_HandLabel_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_Tape_00` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_Tape_01` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Vhs_Tape_02` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Walkman_Body` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallClock_Face` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_03` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_04` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_05` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_06` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_07` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_08` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Cd_09` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `WallShelf_Long` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_BackLeft` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_BackLower` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_BackRight` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_BackUpper` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_Outlet` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wall_Right` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Wastebasket_Main` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Windchime_Cord` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Windchime_Tube_00` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Windchime_Tube_01` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Windchime_Tube_02` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_FrameRail` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_FrameRail.001` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_FrameSide` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_FrameSide.001` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_Mullion` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_Sill` | P0 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Window_Soft` | P0 | 1.5 已摆放 | 预览配置，不导出 | LIGHT |
| `Windowsill_Figurine` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
| `Windowsill_FigurineHead` | P1 | 1.5 已摆放 | 2 精修 / 3 UV烘焙 | MESH |
