import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
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
    { label: 'Shiekhupura', value: 'Shiekhupura' },
    { label: 'Lahore', value: 'Lahore' },
    { label: 'Islamabad', value: 'Islamabad' },
    { label: 'Faisalabad', value: 'Faisalabad' },
  ]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Need Blood</Text>
      <Text style={styles.subtitle}>Find compatible blood donors near you..!!</Text>

      <View>
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
          onPress={() => router.push('/resultscreen')}
        ><Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
   container: { 
    padding: 25,
    justifyContent: "center",
    alignItems: 'center',
    backgroundColor: "#fff",
    flexGrow: 1 
   },
   title: { 
    fontSize: 26, 
    fontWeight: 'bold', 
    color: '#fff', 
    backgroundColor: '#d40000', 
    width: '100%', 
    textAlign: 'center', 
    paddingVertical: 20,
   },
   subtitle: { 
    fontSize: 14, 
    textAlign: 'center', 
    marginVertical: 10, 
    color: '#555' 
   },
   Title: { 
    alignItems: 'center',
    fontSize: 25,
    fontWeight: 'bold', 
    color: '#d40000', 
    marginBottom: 20 
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
