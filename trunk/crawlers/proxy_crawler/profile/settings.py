# 代理爬虫配置文件
proxy_spider_settings = dict(
    PROXY_URL='http://www.xiladaili.com/gaoni/{}/',  # 西拉免费代理网址
    THREAD_POOL_MAX=5,  # 线程池最大数量
    MAX_PAGE=10,  # 爬取页数
)

# 代理验证配置文件
proxy_check_settings = dict(
    VALIDATE_URL='http://icanhazip.com',  # 代理IP验证网址（Get请求会返回请求的IP地址）
    THREAD_POOL_MAX=3,  # 线程池最大数量
)
