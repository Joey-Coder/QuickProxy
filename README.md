## QuickProxy   


### 介绍   

* 简单的，并发的，异步实现的***高匿代理池***  
* 使用redis存储，flask实现对外接口  
* 使用asyncio异步爬取，异步检测，多进程驱动    
* 某宝平台可用代理约为50个   

---

### 使用   
* 配置setting.py中的参数   
* 终端运行    ```python3 main.py```   
* 访问flask:  

|  api   | func  |
|  ----  | ----  |
| host:port/random  | 随机获取一个可用代理 |
| host:port/count  | 查看代理池中代理总数量 |
| host:port/avail  | 查看代理池中可用代理的数量 |
 
  


