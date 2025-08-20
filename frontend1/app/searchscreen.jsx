import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, SafeAreaView } from 'react-native';
import DropDownPicker from 'react-native-dropdown-picker';
import { router } from 'expo-router';

export default function SearchDonorsScreen() {
  const [bloodOpen, setBloodOpen] = useState(false);
  const [bloodValue, setBloodValue] = useState(null);
  const [bloodItems, setBloodItems] = useState([
    { label: 'A+', value: 'A+' },
    { label: 'A-', value: 'A-' },
    { label: 'B+', value: 'B+' },
    { label: 'B-', value: 'B-' },
    { label: 'O+', value: 'O+' },
    { label: 'O-', value: 'O-' },
    { label: 'AB+', value: 'AB+' },
    { label: 'AB-', value: 'AB-' },
  ]);

  const [cityOpen, setCityOpen] = useState(false);
  const [cityValue, setCityValue] = useState(null);
  const [cityItems, setCityItems] = useState([
    { label: 'Sheikhupura', value: 'Sheikhupura' },
    { label: 'Lahore', value: 'Lahore' },
    { label: 'Islamabad', value: 'Islamabad' },
    { label: 'Faisalabad', value: 'Faisalabad' },
  ]);

  const handleSearch = () => {
    if (!bloodValue || !cityValue) {
      Alert.alert('Validation Error', 'Please select both blood group and city.');
      return;
    }

    // Navigate to donor list screen with search parameters
    router.push({
      pathname: '/donorlist',
      params: {
        bloodGroup: bloodValue,
        city: cityValue,
      },
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Need Blood</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.subtitle}>Find compatible blood donors near you..!!</Text>
        <Text style={styles.Title}>Search Donors</Text>

        <Text style={styles.label}>Search by Blood Type</Text>
        <DropDownPicker
          open={bloodOpen}
          value={bloodValue}
          items={bloodItems}
          setOpen={setBloodOpen}
          setValue={setBloodValue}
          setItems={setBloodItems}
          placeholder="Select Blood Type"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
        />

        <Text style={styles.label}>Search by City</Text>
        <DropDownPicker
          open={cityOpen}
          value={cityValue}
          items={cityItems}
          setOpen={setCityOpen}
          setValue={setCityValue}
          setItems={setCityItems}
          placeholder="Select City"
          style={styles.dropdown}
          dropDownContainerStyle={styles.dropdownContainer}
        />

        <TouchableOpacity
          style={styles.searchButton}
          onPress={handleSearch}
        ><Text style={styles.searchButtonText}>Search Donors</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
   container: { 
    flex: 1,
    backgroundColor: "#fff",
   },
   header: {
    backgroundColor: '#d40000',
    paddingVertical: 15,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#2c0101',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
   },
   backButton: {
    marginRight: 15,
   },
   backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
   },
   title: { 
    fontSize: 20, 
    fontWeight: 'bold', 
    color: '#fff', 
    flex: 1,
   },
   content: {
    padding: 25,
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
   },
   subtitle: { 
    fontSize: 16, 
    color: '#666', 
    marginBottom: 30, 
    textAlign: 'center' 
   },
   Title: { 
    fontSize: 20, 
    fontWeight: 'bold', 
    color: '#333', 
    marginBottom: 20, 
    textAlign: 'center' 
   },
   label: { 
    fontWeight: "bold",
    marginTop: 10,
    marginBottom: 5,
    color: "#333",  
   },
   dropdown: { 
    backgroundColor: "#f2f2f2",
    marginBottom: 5,
    borderWidth: 1,
    borderColor: "#f2f2f2", 
   },
   dropdownContainer: { 
    backgroundColor: '#fcf7f7ff',
   },
   searchButton: {
    backgroundColor: '#d40000',
    padding: 12,
    borderRadius: 25,
    marginTop: 30,
    alignItems: 'center',
    shadowColor: '#d40000',
    shadowOffset: {
      width: 0,
      height: 3,
    },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 5,
    width: '60%',
   },
   searchButtonText: { 
    color: '#fff', 
    fontSize: 16, 
    fontWeight: 'bold' 
 },
});
