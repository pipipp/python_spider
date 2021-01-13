# 代理爬虫配置文件
proxy_spider_settings = dict(
    PROXY_URL='http://www.xiladaili.com/https/{}/',  # 西拉免费代理网址（获取https协议代理）
    THREAD_POOL_MAX=5,  # 线程池最大数量（1个线程爬取1页数据）
    MAX_PAGE=20,  # 爬取页数
)

# 代理验证配置文件
proxy_check_settings = dict(
    VALIDATE_URL='https://www.baidu.com/',  # 代理IP验证网址
    THREAD_POOL_MAX=5,  # 线程池最大数量（1个线程验证一个代理IP信息）
)
