#coding:utf-8
#File: Cfg.py
#Auth: lixp(@500wan.com)
#Date: 2014-09-11 16:54:28
#Desc: 

class CFG(object):
    
    _instance = None

    def __init__(self):
        self._dict = {}

    @classmethod
    def get_instance(cls, *args, **kwargs):
        """单例"""
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
        
    def load_conf(self, conf_file):
        """载入文件"""
        with open(conf_file, 'r') as f:
            Ls = f.readlines() 

        LLs = []
        for L in Ls:
            LL = self.__filter(L[:-1],'#')
            if LL:
                LLs.append(LL)

        self.__gen_dict(LLs)

    def __filter(self, str, separator='#'):
        """过滤注释"""
        if len(str) == 0:
            return None
        n = str.find(separator)
        if n==0:
            return None
        if n==-1:
            return str 
        return str[:n]


    def __gen_dict(self,LLs):
        """文本生成字典，最多支持两层目录"""
        key = None 
        val = {}
        dkey = None
        dval = {}
        dd   = {}
        for LL in LLs:
            lb = LL.find('[')
            rb = LL.find(']')
            if lb != -1 and rb != -1:
                dot = LL.find('.')
                if dot != -1:
                    if dkey:
                        dd.update({dkey:dval})     
                        self._dict.update({key:dd})
                    dkey = LL[dot+1:rb].strip() 
                    dval = {}
                else:
                    if dkey:
                        dd.update({dkey:dval})     
                        self._dict.update({key:dd})
                        dkey = None
                        dval = {}
                    elif key:
                        self._dict.update({key:val})
                    key = LL[lb+1:rb].strip()
                    val = {}
            else:
                n = LL.find(':')
                if n != -1:
                    d = {LL[0:n].strip() : LL[n+1:].strip()}
                    if dkey:
                        dval.update(d)
                    else:
                        val.update(d)
        if dkey:
            dd.update({dkey:dval})
            self._dict.update({key:dd})
        elif key:
            self._dict.update({key:val})
        
        
    
    def get(self, *args):
        """获取索引数据
            默认返回整个cfg字典
            支持 cfg.get('foo', 'bar')
            支持 cfg.get('foo/bar')

        """
        if not args:
            return self._dict
        is_tree_style = repr(args).find(r'/') != -1
        if is_tree_style and len(args) > 1:
            raise ValueError('args error')
        elif is_tree_style and len(args) == 1:
            params = tuple(args[0].split(r'/'))
        else:
            params = args
        d = self._dict
        for p in params:
            d = self.__get(p, d)
            if not d:
                break;
        return d

    def __get(self, key, d):
        return d.get(key, None)
            
        
if __name__ == '__main__':
    cfg = CFG.get_instance()
    cfg.load_conf('README.md')
    print cfg.get()
    print cfg.get('File','log_dir')
    print cfg.get('Service/svr_name2')



