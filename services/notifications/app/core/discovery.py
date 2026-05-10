import random
import consul

c = consul.Consul(host="nebori-consul", port=8500)

def get_service_url(service_name: str) -> str:
    """
    Звертається до Consul, знаходить всі доступні репліки сервісу,
    і випадковим чином обирає одну (Client-Side Load Balancing / Ribbon).
    """
    # Запитуємо в Consul: "Дай всі інстанси цього сервісу"
    _, services = c.health.service(service_name, passing=True)
    
    if not services:
        raise Exception(f"Сервіс {service_name} не знайдено в Consul!")

    # РЕАЛІЗАЦІЯ LOAD BALANCER (Випадковий вибір зі списку - Random Rule)
    node = random.choice(services)
    
    address = node['Service']['Address']
    port = node['Service']['Port']
    
    return f"http://{address}:{port}/api/v1" if service_name == "achievements-service" else f"http://{address}:{port}"
