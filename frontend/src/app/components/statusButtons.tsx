'use client';
import React, { useState } from 'react';
import './statusButton.css';
import { useSearchParams, usePathname, useRouter } from 'next/navigation';

import 'material-symbols';
import { Button } from '@/components/ui/button';


export default function StatusButtons() {
    const searchParams = useSearchParams()
    const router = useRouter()
    const pathname = usePathname()

    const [selectedStatus, setSelectedStatus] = useState<string>(
        searchParams.get("status") ?? ""
    );

    const isSelected = (statusId: string) => selectedStatus === statusId;

    const filterStatus = (e: React.MouseEvent<HTMLButtonElement>, value: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (selectedStatus === value && value !== "0") {
          setSelectedStatus("0");

          params.delete("status");
          params.set("status", "0");
          
        } else {
          setSelectedStatus(value);
          params.set("status", value);
          e.currentTarget.focus();
        }
      
        router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    };
    return (
        <div className={`statusButton`}>
            <h2>Filter by: </h2>
            <Button onClick={(e) => filterStatus(e, "0")} style={isSelected("0") ? { backgroundColor: 'var(--main_color)', color: 'var(--light_background)' } : {}}  size={"lg"}>
                Active
            </Button>
            <Button onClick={(e) => filterStatus(e, "1")} style={isSelected("1") ? { backgroundColor: 'var(--main_color)', color: 'var(--light_background)' } : {}}   size={"lg"}>
                Charged
            </Button>
            <Button onClick={(e) => filterStatus(e, "2")} style={isSelected("2") ? { backgroundColor: 'var(--main_color)', color: 'var(--light_background)' } : {}}   size={"lg"}>
                Responded
            </Button>
            <Button onClick={(e) => filterStatus(e, "3")} style={isSelected("3") ? { backgroundColor: 'var(--main_color)', color: 'var(--light_background)' } : {}}   size={"lg"}>
                Expired
            </Button>
        </div>
    );
}
