from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    TEST_DATABASE_NAME: str
    DATABASE_ROOT_USER: str
    DATABASE_ROOT_PASSWORD: str
    DO_API_KEY: str
    VCENTER_HOST: str
    VCENTER_USER: str
    VCENTER_PASSWORD: str
    TEMPLATE_NAME: str
    DATASTORE_NAME: str 
    DATACENTER_NAME: str 
    ESXI_HOSTNAME: str
    CUSTOMIZATION_SPEC_NAME: str
    DO_USERNAME : str
    USERNAME: str
    PASSWORD: str
    CLUSTER_NAME: str
    SSH_KEY_PATH: str
    SSH_KEY_ID: int
    IMAGE: str
    REGION: str
    SIZE_SLUG: str
    VPC_UUID: str
    DOMAIN_NAME: str
    LB_IP: str
    REVERSE_PROXY_IP: str
    PROMETHEUS_IP: str


    class Config:
        env_file = ".env"



settings = Settings()