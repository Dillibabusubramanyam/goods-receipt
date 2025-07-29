#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, date
from typing import Dict, Any

class InventoryAPITester:
    def __init__(self, base_url="https://b1d9df1e-05ee-465e-b503-50c881c00f6c.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {}

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict[Any, Any] = None, files: Dict[str, Any] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'id' in response_data:
                        print(f"   Created resource ID: {response_data['id']}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        if success:
            expected_keys = ['total_materials', 'total_locations', 'pending_invoices', 'total_receipts', 'total_issues']
            for key in expected_keys:
                if key not in response:
                    print(f"   ⚠️  Missing key in stats: {key}")
                    return False
            print(f"   📊 Stats: {response}")
        return success

    def test_create_location(self):
        """Test location creation"""
        location_data = {
            "plant_code": "P001",
            "plant_name": "Main Plant",
            "storage_location": "SL01",
            "description": "Main storage location"
        }
        
        success, response = self.run_test(
            "Create Location",
            "POST",
            "locations",
            200,
            data=location_data
        )
        
        if success and 'id' in response:
            self.created_resources['location_id'] = response['id']
            print(f"   📍 Created location: {response['plant_code']} - {response['storage_location']}")
        
        return success

    def test_get_locations(self):
        """Test getting all locations"""
        success, response = self.run_test(
            "Get Locations",
            "GET",
            "locations",
            200
        )
        
        if success:
            print(f"   📍 Found {len(response)} locations")
            
        return success

    def test_create_material(self):
        """Test material creation"""
        material_data = {
            "material_code": "MAT001",
            "material_description": "Test Material 001",
            "material_group": "RAW_MATERIALS",
            "unit_of_measure": "PC"
        }
        
        success, response = self.run_test(
            "Create Material",
            "POST",
            "materials",
            200,
            data=material_data
        )
        
        if success and 'id' in response:
            self.created_resources['material_id'] = response['id']
            print(f"   🧱 Created material: {response['material_code']} - {response['material_description']}")
        
        return success

    def test_get_materials(self):
        """Test getting all materials"""
        success, response = self.run_test(
            "Get Materials",
            "GET",
            "materials",
            200
        )
        
        if success:
            print(f"   🧱 Found {len(response)} materials")
            
        return success

    def test_create_purchase_order(self):
        """Test purchase order creation"""
        po_data = {
            "po_number": "PO001",
            "vendor_code": "V001",
            "vendor_name": "Test Vendor",
            "po_date": date.today().isoformat()
        }
        
        success, response = self.run_test(
            "Create Purchase Order",
            "POST",
            "purchase-orders",
            200,
            data=po_data
        )
        
        if success and 'id' in response:
            self.created_resources['po_id'] = response['id']
            print(f"   📋 Created PO: {response['po_number']} - {response['vendor_name']}")
        
        return success

    def test_get_purchase_orders(self):
        """Test getting all purchase orders"""
        success, response = self.run_test(
            "Get Purchase Orders",
            "GET",
            "purchase-orders",
            200
        )
        
        if success:
            print(f"   📋 Found {len(response)} purchase orders")
            
        return success

    def test_create_invoice(self):
        """Test invoice creation"""
        invoice_data = {
            "invoice_number": "INV001",
            "vendor_code": "V001",
            "vendor_name": "Test Vendor",
            "invoice_date": date.today().isoformat(),
            "invoice_amount": 1000.50
        }
        
        success, response = self.run_test(
            "Create Invoice",
            "POST",
            "invoices",
            200,
            data=invoice_data
        )
        
        if success and 'id' in response:
            self.created_resources['invoice_id'] = response['id']
            print(f"   🧾 Created invoice: {response['invoice_number']} - ${response['invoice_amount']}")
        
        return success

    def test_get_invoices(self):
        """Test getting all invoices"""
        success, response = self.run_test(
            "Get Invoices",
            "GET",
            "invoices",
            200
        )
        
        if success:
            print(f"   🧾 Found {len(response)} invoices")
            
        return success

    def test_create_goods_receipt(self):
        """Test goods receipt creation"""
        if 'material_id' not in self.created_resources or 'location_id' not in self.created_resources:
            print("❌ Cannot test goods receipt - missing material or location")
            return False
            
        gr_data = {
            "po_id": self.created_resources.get('po_id'),
            "po_number": "PO001",
            "invoice_id": self.created_resources.get('invoice_id'),
            "vendor_code": "V001",
            "vendor_name": "Test Vendor",
            "location_id": self.created_resources['location_id'],
            "posting_date": date.today().isoformat(),
            "document_date": date.today().isoformat(),
            "header_text": "Test goods receipt",
            "items": [
                {
                    "material_id": self.created_resources['material_id'],
                    "material_code": "MAT001",
                    "quantity": 100.0,
                    "unit_price": 10.50,
                    "total_amount": 1050.0
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Goods Receipt",
            "POST",
            "goods-receipts",
            200,
            data=gr_data
        )
        
        if success and 'id' in response:
            self.created_resources['gr_id'] = response['id']
            print(f"   📦 Created goods receipt: {response['document_number']}")
        
        return success

    def test_get_goods_receipts(self):
        """Test getting all goods receipts"""
        success, response = self.run_test(
            "Get Goods Receipts",
            "GET",
            "goods-receipts",
            200
        )
        
        if success:
            print(f"   📦 Found {len(response)} goods receipts")
            
        return success

    def test_create_goods_issue(self):
        """Test goods issue creation"""
        if 'material_id' not in self.created_resources or 'location_id' not in self.created_resources:
            print("❌ Cannot test goods issue - missing material or location")
            return False
            
        gi_data = {
            "movement_type": "201",  # Goods Issue for Consumption
            "location_id": self.created_resources['location_id'],
            "posting_date": date.today().isoformat(),
            "document_date": date.today().isoformat(),
            "header_text": "Test goods issue",
            "items": [
                {
                    "material_id": self.created_resources['material_id'],
                    "material_code": "MAT001",
                    "quantity": 50.0,
                    "cost_center": "CC001"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Goods Issue",
            "POST",
            "goods-issues",
            200,
            data=gi_data
        )
        
        if success and 'id' in response:
            self.created_resources['gi_id'] = response['id']
            print(f"   📤 Created goods issue: {response['document_number']}")
        
        return success

    def test_get_goods_issues(self):
        """Test getting all goods issues"""
        success, response = self.run_test(
            "Get Goods Issues",
            "GET",
            "goods-issues",
            200
        )
        
        if success:
            print(f"   📤 Found {len(response)} goods issues")
            
        return success

    def test_get_stock_overview(self):
        """Test stock overview"""
        success, response = self.run_test(
            "Get Stock Overview",
            "GET",
            "stock-overview",
            200
        )
        
        if success:
            print(f"   📊 Found {len(response)} stock items")
            for item in response:
                print(f"      {item['material_code']}: {item['current_quantity']} {item['unit_of_measure']}")
            
        return success

    def test_get_stock_movements(self):
        """Test stock movements"""
        success, response = self.run_test(
            "Get Stock Movements",
            "GET",
            "stock-movements",
            200
        )
        
        if success:
            print(f"   📈 Found {len(response)} stock movements")
            
        return success

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Inventory Management System API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Test sequence - order matters for dependencies
        test_sequence = [
            self.test_dashboard_stats,
            self.test_create_location,
            self.test_get_locations,
            self.test_create_material,
            self.test_get_materials,
            self.test_create_purchase_order,
            self.test_get_purchase_orders,
            self.test_create_invoice,
            self.test_get_invoices,
            self.test_create_goods_receipt,
            self.test_get_goods_receipts,
            self.test_get_stock_overview,
            self.test_create_goods_issue,
            self.test_get_goods_issues,
            self.test_get_stock_movements,
        ]

        for test_func in test_sequence:
            try:
                test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")

        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed.")
            return 1

def main():
    tester = InventoryAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())