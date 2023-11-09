# Schema management 

- Подготовка
    
    1. Переписать сервисы под добавление кастомных сервисов. Сделать отдельным расширением. Можно подумать, оставлять ли всё в GraphManager или как-то иначе. Но для начала сойдёт  и так.

g.call('shema_manager').with('method', 'makePropertyKey').with('name', 'NewName')
g.call('shema_manager').with('method', 'addProperties').with('name', 'NewName')


в yaml-файле лежат пути к конфигам сервисов а в конфигах сервисов лежат 

Хранить конфиг сервисов в 
    - отдельном .yaml файле
    - файле конфига сервера
    - файле конфига графа
    


create graph 

    create serviceRegistry 

        for ever service_file in services_files

            get service factory

            register service in serviceReg

хранить конфиги всех сервисов в properties-файле 




Что надо ещё сделать? 

А что хотим в итоге? 
    
1. Автомл


2. Копию 

