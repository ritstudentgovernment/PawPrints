# PawPrints Components

This folder contains reusable components for the PawPrints platform. These components are designed to provide a consistent and modular structure for building the user interface of the application.

---

## Table of Contents

- [Overview](#overview)
- [Components](#components)
  - [ClientAuthWrapper](#clientauthwrapper)
  - [Footer](#footer)
  - [LoginButton](#loginbutton)
  - [NavBar](#navbar)
  - [Petition](#petition)
  - [PetitionContainer](#petitioncontainer)
  - [PetitionDetail](#petitiondetail)
  - [PetitionEmpty](#petitionempty)
  - [PetitionList](#petitionlist)
  - [Sidebar](#sidebar)
  - [SignButton](#signbutton)
  - [Tag](#tag)
- [Styling](#styling)
- [How to Use](#how-to-use)

---

## Overview

The components in this folder are designed to handle various parts of the PawPrints platform, such as navigation, petition management, and user authentication. Each component is modular and reusable, making it easy to maintain and extend the application.

---

## Components

### **ClientAuthWrapper**
- **File**: `ClientAuthWrapper.tsx`
- **Purpose**: Wraps the application to handle user authentication. Automatically logs in the user on page load.
- **Usage**:
  ```tsx
  import ClientAuthWrapper from './ClientAuthWrapper';

  export default function App() {
      return (
          <ClientAuthWrapper>
              <YourApp />
          </ClientAuthWrapper>
      );
  }
  ```

---

### **Footer**
- **File**: `Footer.tsx`
- **Purpose**: Displays the footer with navigation links and branding.
- **Usage**:
  ```tsx
  import Footer from './Footer';

  export default function ExamplePage() {
      return (
          <div>
              {/* Other content */}
              <Footer />
          </div>
      );
  }
  ```

---

### **LoginButton**
- **File**: `LoginButton.tsx`
- **Purpose**: Handles user login and logout functionality. Displays a login button if the user is not logged in, or a profile link if logged in.
- **Usage**:
  ```tsx
  import LoginButton from './LoginButton';

  export default function NavBar() {
      return (
          <div>
              <LoginButton />
          </div>
      );
  }
  ```

---

### **NavBar**
- **File**: `NavBar.tsx`
- **Purpose**: Displays the navigation bar with links to key sections of the application and the login button.
- **Usage**:
  ```tsx
  import NavBar from './NavBar';

  export default function ExamplePage() {
      return (
          <div>
              <NavBar />
              {/* Page content */}
          </div>
      );
  }
  ```

---

### **Petition**
- **File**: `Petition.tsx`
- **Purpose**: Represents a single petition card with details like title, description, and progress bar.
- **Usage**:
  ```tsx
  import Petition from './Petition';

  export default function ExamplePage({ petitions }) {
      return (
          <div>
              {petitions.map((petition) => (
                  <Petition key={petition.id} p={petition} isLoggedIn={true} />
              ))}
          </div>
      );
  }
  ```

---

### **PetitionContainer**
- **File**: `PetitionContainer.tsx`
- **Purpose**: Fetches and displays a list of petitions. Handles filtering by query, committee, or status.
- **Usage**:
  ```tsx
  import PetitionContainer from './PetitionContainer';

  export default function ExamplePage() {
      return (
          <PetitionContainer query="example" />
      );
  }
  ```

---

### **PetitionDetail**
- **File**: `PetitionDetail.tsx`
- **Purpose**: Displays detailed information about a petition, including updates and a button to sign the petition.
- **Usage**:
  ```tsx
  import dynamic from 'next/dynamic';
  
  const PetitionDetail = dynamic(() => import('./PetitionDetail'), {
    ssr: false,
    loading: () => <p>Loading petition...</p>
  });

  export default function ExamplePage({ petition }) {
      return (
          <PetitionDetail p={petition} isLoggedIn={true} onSign={() => console.log('Signed!')} />
      );
  }
  ```

---

### **PetitionEmpty**
- **File**: `PetitionEmpty.tsx`
- **Purpose**: Displays a message when no petitions are found.
- **Usage**:
  ```tsx
  import PetitionEmpty from './PetitionEmpty';

  export default function ExamplePage() {
      return <PetitionEmpty />;
  }
  ```

---

### **PetitionList**
- **File**: `PetitionList.tsx`
- **Purpose**: Displays a list of petitions with infinite scrolling.
- **Usage**:
  ```tsx
  import PetitionList from './PetitionList';

  export default function ExamplePage({ petitions }) {
      return (
          <PetitionList initialData={petitions} />
      );
  }
  ```

---

### **Sidebar**
- **File**: `Sidebar.tsx`
- **Purpose**: Displays a sidebar with a dropdown to filter petitions by committee.
- **Usage**:
  ```tsx
  import Sidebar from './Sidebar';

  export default function ExamplePage({ committees }) {
      return <Sidebar committees={committees} />;
  }
  ```

---

### **SignButton**
- **File**: `SignButton.tsx`
- **Purpose**: Button to sign a petition. Calls an API to register the signature.
- **Usage**:
  ```tsx
  import SignButton from './SignButton';

  export default function ExamplePage({ petitionID }) {
      return <SignButton petitionID={petitionID} onSign={() => console.log('Signed!')} />;
  }
  ```

---

### **Tag**
- **File**: `Tag.tsx`
- **Purpose**: Displays a tag for a committee or category.
- **Usage**:
  ```tsx
  import Tag from './Tag';

  export default function ExamplePage({ committees }) {
      return (
          <div>
              {committees.map((committee) => (
                  <Tag key={committee.name} name={committee.name} description={committee.description} />
              ))}
          </div>
      );
  }
  ```

---

## Styling

Each component has an associated CSS file for styling. These files are located in the same directory as the components and follow a consistent naming convention (e.g., `Footer.tsx` uses `footer.css`).

---

## How to Use

1. **Import the Component**:
   Import the desired component into your file:
   ```tsx
   import ComponentName from './ComponentName';
   ```

2. **Pass Props**:
   Pass the required props to the component. Refer to the usage examples for each component.

3. **Add to Your Layout**:
   Include the component in your page or layout as needed.
