import sys
import yaml
import json

def schema_validation(schema_file, tenant_yaml_file):
    with open(schema_file, "r") as schema_f:
        schema_yaml_data = yaml.safe_load(schema_f)

    with open(tenant_yaml_file, "r") as tenant_f:
        tenant_yaml_data = yaml.safe_load(tenant_f)

    if type(tenant_yaml_data) is not dict:
        print(f"Invalid yaml")
        sys.exit(1)

    required_keys = []
    allowed_keys = []

    for key, value in schema_yaml_data.items():
        if type(value) is dict:
            allowed_keys.append(key)          # FIX: always allow schema-defined keys
            for k, v in value.items():
                if k == "required" and v == True:
                    required_keys.append(key)

    # FIX: no need to build tenant_required_keys list
    for key in required_keys:
        if key not in tenant_yaml_data:
            print(f"Invalid/missing required key: {key}")
            sys.exit(1)

    for key in tenant_yaml_data:
        if key not in allowed_keys:
            print(f"Invalid top-level key: {key}. Allowed keys: {allowed_keys}")
            sys.exit(1)

    # Check env
    allowed_envs = schema_yaml_data["env"]["allowed"]
    if tenant_yaml_data["env"] not in allowed_envs:
        print(f"Invalid environment value: {tenant_yaml_data['env']}")
        sys.exit(1)

    # Check region
    allowed_regions = schema_yaml_data["region"]["allowed"]
    if tenant_yaml_data["region"] not in allowed_regions:
        print(f"Invalid region value: {tenant_yaml_data['region']}")
        sys.exit(1)

    # Validate services
    if type(tenant_yaml_data["services"]) is not dict:
        print(f"Invalid services block!")
        sys.exit(1)

    allowed_services = []
    for service in schema_yaml_data["services"].keys():
        allowed_services.append(service)

    for service in tenant_yaml_data["services"].keys():
        if service not in allowed_services:
            print(f"Service not allowed: {service}")
            sys.exit(1)

        # FIX: ensure service config is dict
        if type(tenant_yaml_data["services"][service]) is not dict:
            print(f"Invalid service config (must be dict): {service}")
            sys.exit(1)

        if "enabled" not in tenant_yaml_data["services"][service]:
            print(f"Missing 'enabled' for service: {service}")
            sys.exit(1)

        if tenant_yaml_data["services"][service]["enabled"] not in [True, False]:
            print(f"'enabled' must be boolean for service: {service}")
            sys.exit(1)

    print("✅ Step 3 validation passed")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test.py <schema_file_path> <yaml_file_path>")
        sys.exit(1)

    schema_validation(sys.argv[1], sys.argv[2])
