import requests, os, re, json, shutil


# 通过Steam API下载appid对应的名称
def down_steam_dict():
    api_url = r'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
    res = requests.get(api_url)
    if res and len(res.content) > 65535:
        with open(r'appid.json', 'wb')as f:
            f.write(res.content)
        return True
    else:
        print('下载steam appid dict失败')
        return False


def run():
    if not os.path.exists(r'appid.json'):
        print('未发现appid.json，即将重新下载')
        if not down_steam_dict():
            return False
    with open(r'appid.json', encoding='utf-8')as f:
        appid_list = json.loads(f.read())['applist']['apps']['app']
    app_info = {}
    for appid_dict in appid_list:
        app_info[str(appid_dict['appid'])] = appid_dict['name']


    # 如果存在我们自定义的rename.json，则使用该文件中定义的名称
    if os.path.exists(r'rename.json'):
        with open(r'rename.json', encoding='utf-8')as f:
            rename_list = json.loads(f.read())
        for appid_dict in rename_list:
            appid = str(appid_dict['appid']) 
            if not appid in app_info.keys():
                print('本地appid.json中无游戏appid=%s的相关信息，即将重新下载steam appid dict' % appid)
                if down_steam_dict():
                    run()
                    return

            # 如果此前创建了官方游戏名称的文件夹，则重命名成我们自定义的名称
            app_name = app_info[str(appid_dict['appid'])]
            app_name = re.sub(r'[\\\*\?\|/:"<>\.]', '', app_name)
            official_path = os.path.join(pic_dir, app_name)
            rename_path = os.path.join(pic_dir, appid_dict['name'])

            if os.path.exists(official_path):
                if not os.path.exists(rename_path):
                    os.rename(official_path, rename_path)
                    print('重命名文件夹：%s -> %s' % (official_path, rename_path))
                else:
                    pic_files = os.listdir(official_path)         
                    for file in pic_files:
                        file_path = os.path.join(official_path, file)   
                        if os.path.isfile(file_path):
                            if os.path.exists(os.path.join(rename_path, file)):
                                print("%s中已存在%s，跳过，不移动" % (rename_path, file))
                                continue
                            else:
                                shutil.move(file_path, rename_path)
                                print('移动文件[%s] %s' % (appid_dict['name'], file))
                    os.removedirs(official_path)
                    print('删除文件夹%s' % official_path)

            # 其他的单个图片此后也用我们自定义的名称
            app_info[str(appid_dict['appid'])] = appid_dict['name']


    # 列出当前文件夹所有文件（夹），不递归子文件夹
    files = os.listdir(pic_dir)
    for file in files:
        res = re.search(r'^(\d+?)_(\d+?)_\d+?.png$', file)
        if not res:
            continue
        appid, time = res.group(1), res.group(2)
        
        if appid in app_info.keys():
            app_name = app_info[appid]
            app_name = re.sub(r'[\\\*\?\|/:"<>\.]', '', app_name)
            
            new_path = os.path.join(pic_dir, app_name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)

            # 移动文件
            old_file = os.path.join(pic_dir, file)
            new_file = os.path.join(new_path, file)
            shutil.move(old_file, new_file)
            print('移动文件[%s] %s' % (app_name, file))

        else:
            print('本地appid.json中无游戏appid=%s的相关信息，即将重新下载steam appid dict' % appid)
            if down_steam_dict():
                run()


if __name__ == '__main__':
    pic_dir = r'D:\图片\steam'
    run()