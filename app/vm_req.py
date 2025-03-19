from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
from .config import settings


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    container.Destroy()
    return obj

def deploy_vm(vm_name):
    context = ssl._create_unverified_context()
    si = SmartConnect(host=settings.VCENTER_HOST, user=settings.VCENTER_USER, pwd=settings.VCENTER_PASSWORD, sslContext=context)
    content = si.RetrieveContent()

    datacenter = get_obj(content, [vim.Datacenter], settings.DATACENTER_NAME)
    if not datacenter:
        print(f"Datacenter {settings.DATACENTER_NAME} not found!")
        Disconnect(si)
        return
    
    host = get_obj(content, [vim.HostSystem], settings.ESXI_HOSTNAME)
    if not host:
        print(f"ESXi Host {settings.ESXI_HOSTNAME} not found!")
        Disconnect(si)
        return

    resource_pool = host.parent.resourcePool  

    datastore = get_obj(content, [vim.Datastore], settings.DATASTORE_NAME)
    if not datastore:
        print(f"Datastore {settings.DATASTORE_NAME} not found!")
        Disconnect(si)
        return

    template = get_obj(content, [vim.VirtualMachine], settings.TEMPLATE_NAME)
    if not template:
        print(f"Template {settings.TEMPLATE_NAME} not found!")
        Disconnect(si)
        return

    folder = datacenter.vmFolder  
    customization_spec_manager = content.customizationSpecManager
    customization_spec = customization_spec_manager.GetCustomizationSpec(name=settings.CUSTOMIZATION_SPEC_NAME)

    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = vim.vm.RelocateSpec()
    clone_spec.location.datastore = datastore
    clone_spec.location.pool = resource_pool
    clone_spec.powerOn = True  

    if customization_spec:
        clone_spec.customization = customization_spec.spec

    task = template.Clone(folder=folder, name=vm_name, spec=clone_spec)
    print(f"Cloning {settings.TEMPLATE_NAME} to {vm_name} on {settings.ESXI_HOSTNAME}...")

    while task.info.state == vim.TaskInfo.State.running:
        continue  

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM {vm_name} created successfully with customization!")
    else:
        print(f"VM creation failed: {task.info.error}")

    Disconnect(si)



def delete_vm(vm_name):
    context = ssl._create_unverified_context()

    si = SmartConnect(host=settings.VCENTER_HOST, user=settings.VCENTER_USER, pwd=settings.VCENTER_PASSWORD, sslContext=context)
    content = si.RetrieveContent()

    vm = get_obj(content, [vim.VirtualMachine], vm_name)
    if not vm:
        print(f"VM {vm_name} not found!")
        Disconnect(si)
        return

    print(f"Found VM: {vm_name}, proceeding with deletion...")

    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        print(f"Powering off VM {vm_name}...")
        task = vm.PowerOffVM_Task()
        while task.info.state == vim.TaskInfo.State.running:
            continue  

    print(f"Deleting VM {vm_name}...")
    task = vm.Destroy_Task()
    while task.info.state == vim.TaskInfo.State.running:
        continue  

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM {vm_name} deleted successfully!")
    else:
        print(f"Failed to delete VM {vm_name}: {task.info.error}")

    Disconnect(si)
