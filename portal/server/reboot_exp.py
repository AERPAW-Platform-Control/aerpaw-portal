import os
from django.core.exceptions import ValidationError
from django.http import HttpRequest, QueryDict
from rest_framework.request import Request

from portal.apps.experiments.api.viewsets import ExperimentViewSet, CanonicalExperimentResourceViewSet
from portal.apps.resources.api.viewsets import ResourceViewSet
from portal.apps.users.models import AerpawUser
from portal.server.ops_ssh_utils import AerpawSsh
from portal.server.settings import MOCK_OPS

aerpaw_ops_host = os.getenv('AERPAW_OPS_HOST')
aerpaw_ops_port = os.getenv('AERPAW_OPS_PORT')
aerpaw_ops_user = os.getenv('AERPAW_OPS_USER')
aerpaw_ops_key_file = os.getenv('AERPAW_OPS_KEY_FILE')

""" 
Experiment 851
sudo /home/aerpawops/AERPAW-Dev/DCS/AP-VE-SN/utils/ap-restore-container-networking.sh Experimenter 851 5 0 LW1 LW2 LW3 LW4 aprn vehicle_uav 4.3 afrn vehicle_uav 4.3 afrn vehicle_none 4.3 afrn vehicle_none 4.3 afrn vehicle_none 4.3
sudo docker exec E-VM-X0851-M1 service ssh start
sudo docker exec E-VM-X0851-M2 service ssh start
sudo docker exec E-VM-X0851-M3 service ssh start
sudo docker exec E-VM-X0851-M4 service ssh start
sudo docker exec E-VM-X0851-M5 service ssh start
sudo docker exec OEO-CONSOLE-X0851 service ssh start
sudo docker exec OEO-CONSOLE-X0851 /root/firstrun.sh
sudo docker exec OEO-SERVER-X0851 /root/firstrun.sh
sudo docker exec C-VM-X0851-M1 /root/firstrun.sh
sudo docker exec C-VM-X0851-M2 /root/firstrun.sh
sudo docker exec C-VM-X0851-M3 /root/firstrun.sh
sudo docker exec C-VM-X0851-M4 /root/firstrun.sh
sudo docker exec C-VM-X0851-M5 /root/firstrun.sh
sudo docker exec CH-EM-VM-X0851 /root/firstrun.sh
 """

class RebootExp():

    def send_command(self, command):
        try:
            ssh_call = AerpawSsh(hostname='152.14.188.15', username='aerpawcf', keyfile='./ssh/aerpawops_id_rsa')
            response, exit_code = ssh_call.send_command(command, verbose=True, mock=False)
        except Exception as exc:
            print(f'An exception occured while running:\n {command}\n\n The exception is: \n{exc}')
            response = exc
            exit_code = 1

        return response, exit_code
    
    def container_clean_up(self, ap_ve_server_ip):
        command = 'sudo AERPAW-Dev/AHN/substrate_config/utils/ap-del-ovs-orphan-ports.sh'
        self.send_command(command, ap_ve_server_ip)
        
    def bring_up_containers_by_canonical_number(self, ap_ve_server_ip, canonical_number):
        command = 'sudo docker ps -a --format "{{.Names}}" | grep X0{}'.format(canonical_number)
        print(command)
        response, exit_code = self.send_command(command, ap_ve_server_ip)
        print(f'Response: {response}')
        print(f'exit_code: {exit_code}')

    def bring_up_containers_before_date(self, ap_ve_server_ip, year_month_day):
        if len(year_month_day) != 10:
            raise ValidationError('Year_month_day must be in the format 0000-00-00')

        command = 'sudo docker ps -a --format "{{.ID}} {{.CreatedAt}}" | awk -v cutoff="$(date -d {} +%s)" {cmd = "date -d " $2 " " $3 " " $4 " +%s"cmd | getline t close(cmd) if (t > cutoff) print $1} | xargs -r sudo docker start'.format(year_month_day)
        self.send_command(command, ap_ve_server_ip)

    def restore_container_networking(self, ap_ve_server_ip, exp_id: int):
        ops_user = AerpawUser.objects.get(id = 316)

        exp_request = Request(request=HttpRequest())
        exp_request.user = ops_user
        exp_viewset = ExperimentViewSet(request=exp_request)
        exp_data = exp_viewset.retrieve(request=exp_request, pk=exp_id).data
        
        canonical_number= exp_data.get("canonical_number")

        request = Request(request=HttpRequest())
        resource_list = []
        request.user = ops_user
        request.query_params.update({'experiment_id': exp_id})
        for res_id in exp_data.get('resources'):
            request.query_params.update({'resource_id': res_id})
            r = CanonicalExperimentResourceViewSet(request=request)
            res = r.list(request=request)
            if res.data:
                resource_list.append(res.data.get('results')[0])
        resource_list.sort(key=lambda x: x.get('experiment_node_number'))

        resource_names = ''
        resource_params = ''
        for resource in resource_list:
            r_name = resource['node_display_name'] if resource['node_type'] != 'aprn' else '0'
            resource_names = f'{resource_names} {r_name}'
            resource_params = resource_params + f' {resource["node_type"]} {resource["node_vehicle"]} {resource["node_uhd"]}'

        command = f'sudo /home/aerpawops/AERPAW-Dev/DCS/AP-VE-SN/utils/ap-restore-container-networking.sh Experimenter {canonical_number} {len(resource_list)}{resource_names}{resource_params}'
        print(f'command= {command}')
        self.send_command(command, ap_ve_server_ip)

    