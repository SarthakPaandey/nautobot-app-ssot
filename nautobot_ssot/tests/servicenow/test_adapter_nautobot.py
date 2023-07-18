"""Unit tests for the Nautobot DiffSync adapter."""

from nautobot.core.testing import TransactionTestCase

from nautobot_ssot.integrations.servicenow.jobs import ServiceNowDataTarget
from nautobot_ssot.integrations.servicenow.diffsync.adapter_nautobot import NautobotDiffSync


class NautobotDiffSyncTestCase(TransactionTestCase):
    """Test the NautobotDiffSync adapter class."""

    databases = ("default", "job_logs")

    def setUp(self):
        """Per-test-case data setup."""
        status_active, _ = Status.objects.get_or_create(name="Active", slug="active")

        region_1 = Region.objects.create(name="Region 1", slug="region-1")
        region_2 = Region.objects.create(name="Region 2", slug="region-2", parent=region_1)
        region_3 = Region.objects.create(name="Site/Region", slug="site-region", parent=region_1)

        site_1 = Site.objects.create(region=region_2, name="Site 1", slug="site-1", status=status_active)
        site_2 = Site.objects.create(region=region_3, name="Site/Region", slug="site-region", status=status_active)

        manufacturer, _ = Manufacturer.objects.get_or_create(name="Cisco", slug="cisco")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="CSR 1000v", slug="csr1000v")
        device_role = DeviceRole.objects.create(name="Router", slug="router")

        device_1 = Device.objects.create(
            name="csr1", device_type=device_type, device_role=device_role, site=site_1, status=status_active
        )
        device_2 = Device.objects.create(
            name="csr2", device_type=device_type, device_role=device_role, site=site_2, status=status_active
        )

        Interface.objects.create(device=device_1, name="eth1", status=status_active)
        Interface.objects.create(device=device_1, name="eth2", status=status_active)
        Interface.objects.create(device=device_2, name="eth1", status=status_active)
        Interface.objects.create(device=device_2, name="eth2", status=status_active)

    def test_data_loading(self):
        """Test the load() function."""
        job = ServiceNowDataTarget()
        job.job_result = JobResult.objects.create(
            name=job.class_path, obj_type=ContentType.objects.get_for_model(Job), user=None, job_id=uuid.uuid4()
        )
        nds = NautobotDiffSync(job=job, sync=None)
        nds.load()

        self.assertEqual(
            ["Region 1", "Region 2", "Site 1", "Site/Region"],
            sorted(loc.get_unique_id() for loc in nds.get_all("location")),
        )
        self.assertEqual(
            ["csr1", "csr2"],
            sorted(dev.get_unique_id() for dev in nds.get_all("device")),
        )
        self.assertEqual(
            ["csr1__eth1", "csr1__eth2", "csr2__eth1", "csr2__eth2"],
            sorted(intf.get_unique_id() for intf in nds.get_all("interface")),
        )
