# xjbx-QQ-group-bot
一个基于NoneBot的xjbx的Q群机器人，完全属于xjb写的范畴。功能很杂乱，包括[nbnhhsh](https://github.com/itorr/nbnhhsh?files=1)、图片搜索、rss订阅等各种乱七八糟的功能。基本上就是我网上看到的和一拍脑袋想出来的功能大杂烩。

# 安装

目前没有考虑安装问题。如果你看得懂源码的话，可以尝试部署一下。后续可能会加入部署功能。

~~然而才发现给自己挖了个大坑，数据库我用的postgreSQL，表啥的都是我手动创的（不要问我为什么用postgreSQL，我也想知道为什么）。所以在看源码的时候你可以先猜一下我表怎么建的，后续我会把表公开。~~

~~当然，在研究可迁移部署的时候，我才发现这个问题，迁移难度++，难受。。。~~

# 好家伙，现在已经迁移到nb2了，宁不试试🐎？[新项目地址](https://github.com/Pzzzzz5142/Pbot)

# Simple Usage

目前该机器人支持以下功能：

+ st

    说明：向机器人发送`st`，然后发送你想搜索的图片。机器人会帮你搜索图片来源。

+ bilibili

    说明：向机器人发送`bilibili`（或者短命令`bili`），再发送你想搜索的内容，机器人会返回根据关键字在b站搜索的结果。群聊默认返回 **1** 个结果，私聊默认返回 **5** 个结果。

+ hhsh

    说明：向机器人发送`hhsh`+你想搜索的汉字首字母简写，以空格分开。机器人会调用 [nbnhhsh](https://github.com/itorr/nbnhhsh) 的api搜索该简写代表的真实含义。如果你对搜索结果不满意，可以去 [这里](https://lab.magiconch.com/nbnhhsh/) 提交新简写及其含义。

+ rss

    说明：该功能用于订阅消息源的消息，该功能基于 [Rsshub](https://github.com/DIYgod/RSSHub)。由于我很懒，所以现在只支持三个订阅源。向机器人发送`rss`，然后按机器人的引导来就行了。同时，加上`-s`参数可以订阅消息源，不加的话就是仅查看最新消息。

+ wm

    说明：该功能用于翻译。采用 NiuTrans api。

+ jrrp

    说明：获取今日人品。（其实底层就是一个randint。。。

+ stock

    说明：群内云炒股。接入 Yahoo Finance api，股票价格实时更新。具体

# Advanced Usage    

由于我很懒，所以高级用法自己看看源码吧（QwQ），但是基本用法已经够用了。

# To-Do

+ stock

    说明：股票交易功能。接入真实的股票数据，来进行群内云炒股。
    
    完成度：基础功能已完成。
    
    To-do：
        
    + ~~优化群内体验，解决刷屏问题。~~ 已完成
    
    + ~~人性化指令~~ 已完成
    
    + float精度问题
   
+ 抽卡

    说明：抽卡功能。卡池由Onedrive在线文档维护。
    
    完成度：（只建立了Onedrive文档
    
    To-do：
    
    + 明日方舟多卡池抽卡，有保底机制。
        
    + 接入股票功能， 使用股票资金抽卡
        
    + Onedrive文档自动抓取群友维护的卡池信息。

+ bilibili 动态 universal add

    说明：可自定义添加想要关注的up主

    完成度：none

    To-do：

    + 完成该功能

# 鸣谢

+ [[开源] 二次元搜图QQ机器人](https://github.com/Tsuk1ko/CQ-picfinder-robot) 一开始就想把这个插件的功能加到我的机器人里面，无奈博主是用我不会的语言写的，既然抄不了就只能自己手撸一个了。当然他的源码也很有启发性，API也很好用！
+ [nbnhhsh](https://github.com/itorr/nbnhhsh) 只能说这玩意太有意思了！（就是访问速度有点不太理想
+ [Rsshub](https://github.com/DIYgod/RSSHub) 整个`rss`都依赖于它了，我怎么能不感谢呢？
+ [SauceNAO](https://saucenao.com) `st`功能有很大一部分都是依赖于它的，同样表示感谢！
+ [哔哩哔哩](https://www.bilibili.com)
+ [nonebot](https://github.com/nonebot/nonebot)
