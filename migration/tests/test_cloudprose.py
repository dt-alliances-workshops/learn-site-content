from migration.claat.cloudprose import scan_cloud_prose


def test_flags_azure_portal_case_insensitive():
    f = scan_cloud_prose("Open the Azure PORTAL and search for the cluster.")
    assert f is not None
    assert f.section == "env"


def test_flags_promo_code():
    f = scan_cloud_prose("You will receive an Azure Pass promo code from staff.")
    assert f is not None


def test_no_flag_when_absent():
    assert scan_cloud_prose("Deploy the operator with kubectl and observe traces.") is None


def test_message_mentions_docs_first():
    f = scan_cloud_prose("Log in with your subscription credentials.")
    assert "docs-first" in f.message.lower()
