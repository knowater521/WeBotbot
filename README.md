# WeBot - wechat遥控&机器人
基于itchat的Wechat机器人，可实现自动回复消息与通过微信控制电脑  
感谢大神提供的itchat库，也感谢github其他大神提供的类似开源项目为小弟打开了大门  
  
原本只是因为晚上忘记关电脑，所以想写一个小工具如果忘记关电脑能自动提醒自己  
后来发现itchat实在好玩，然后就越写越多--  
本人python小菜鸡，功能也是边查边写，再次感谢各位慷慨分享的大佬们~  
为了防止自己忘，代码注释比较详细和啰嗦，共同学习进步~  

[配表版本]代码文件：
WeBot.py - 主程序
setting.xls - 初始配置
配表可实现微信修改表格信息，具体实现也在代码中做了尝试

本版本也封装好了一个可独立运行的exe，与setting表格放在同一目录下即可。
网盘地址：https://pan.baidu.com/s/1p7g5WK8mcq6KMdPXsEWURw 提取码 0edx


[非配表版本]代码文件：  
weBotbot.py - 主程序  
weBotbot_setting.py - 用户权限，回复内容等一些设置项  
  
-2019.08.28-  
第一次上传  
功能点：  
1.定时提醒  
2.自动回复  
3.关机  
4.待机  
5.cmd指令  
**6.远程发送电脑文件到手机**  
    
-2019.08.29-  
第二次上传  
修复若干bug：如查新闻时返回url格式不统一，机器人自己回复自己等  
新功能：  
**1.截屏**（感谢XAS-712）  
**2.远程打开文件**，配合截屏可以简单远程查看及控制电脑  
**3.动态添加新提醒**  
4.机器人实时开关，可**自动回复全部好友**  
**5.增减授权人**  

-2019.09.10- 
修复配表版本若干BUG
  
*使用方式：  
-发送 *cmd|xxx (xxx为命令) 即可执行cmd命令  
-发送 *关机 关闭电脑  
-发送 *待机 进入休眠模式  
-发送 *截屏 查看当前桌面状态  
-发送 *open|dir 打开文件或文件夹  
-发送 *download|dir 下载文件  
-发送 *cd|dir 切换目录  
-发送 *cd|dir 切换目录  
-发送 *plan|0:0:0(时间)|xxx(提醒消息) 可以设定提醒  
-发送 *delplan 可以清空提醒  
-发送 *观诗音来 开启小鸡儿机器人自动回复  
-发送 *观诗音走 关闭小鸡儿机器人自动回复  
-发送 *开大 开启全局的小鸡儿机器人自动聊天，撩全场  
-发送 *闭嘴 关闭小鸡儿机器人自动撩全场  
-发送 *授权|xxx(昵称或备注名或微信号) 添加其为授权人  
-发送 *夺权|xxx(昵称或备注名或微信号) 可取消其授权  
-随便打字，和小鸡儿器人聊天  

