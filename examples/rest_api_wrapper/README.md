Wrapper 功能
1. 封装bson-rpc client的连接、数据请求及解析功能
2. 对外统一以 REST API 的形式暴露服务
3. REST服务通信数据统一为JSON

## Dependencies
1. falcon - rest api framework
2. gunicorn - wsgi http server
3. pytest - unit test 
4. mock - mock client 
5. request - http request
6. aumbry - multi-type configuration library
7. supervisor - system deamon

## Launch Server

1. dev    
默认使用gunicorn启动，会有deamon进程守护    
!! 需要在根目录下手工新建.secret.json配置文件，具体信息参考config.py    
> cd project/root/dir      
> load py_virtual_envs # if nessary        
> pip install aumbry      
> pip install gunicorn       
> gunicorn -c gunicorn.py.ini app       
  

2. production   
生产环境增加supervisord守护      
> pip install supervisor      
> echo_supervisord_conf > supervisord.conf    
> supervisord -c supervisord.conf    

## Run Test

#### Unit tests
> pip install pytest    
> cd project/root/dir    
> pytest tests   

```
tests is where we put test py files
```

#### Functional tests
> pip install requests    
> gunicorn app    
> pytest tests -k test_posted_image_gets_saved    

## TDD
> pip install mock    
> 

