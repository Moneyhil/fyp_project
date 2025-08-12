import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import DropDownPicker from 'react-native-dropdown-picker';
import { useNavigation } from '@react-navigation/native';

export default function SearchDonorsScreen() {
  const navigation = useNavigation();
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
    { label: 'Karachi', value: 'Karachi' },
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
          onPress={() => navigation.navigate('resultsScreen')}
        >
          <Text style={styles.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
   container: { 
    flex: 1, 
    backgroundColor: '#fff', 
    alignItems: 'center', 
    paddingTop: 50   
   },
   title: { 
    fontSize: 26, 
    fontWeight: 'bold', 
    color: '#fff', 
    backgroundColor: '#d40000', 
    width: '100%', 
    textAlign: 'center', 
    paddingVertical: 15
   },
   subtitle: { 
    fontSize: 14, 
    textAlign: 'center', 
    marginVertical: 10, 
    color: '#555' 
   },
   Title: { 
    fontSize: 20, 
    fontWeight: 'bold', 
    color: '#d40000', 
    marginBottom: 20 
   },
   label: { 
    fontSize: 14, 
    color: '#333', 
    marginTop: 10, 
    marginBottom: 5, 
    alignSelf: 'flex-start'  
   },
   dropdown: { 
    borderColor: '#f7f1f1ff', 
    borderWidth: 1, 
    borderRadius: 8, 
    marginBottom: 10 
   },
   dropdownContainer: { 
    borderColor: '#ccc'
   },
   searchButton: {
    backgroundColor: '#d40000',
    paddingVertical: 12,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 10,
    alignItems: 'center',
    boxShadow: '0px 3px 6px rgba(212, 0, 0, 1)',
    width: '60%',
   },
   searchButtonText: { 
    color: '#fff', 
    fontSize: 16, 
    fontWeight: 'bold' 
 },
});
