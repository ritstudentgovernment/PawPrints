'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { API_URL } from '../api/specialRoute';
import { useAuth } from '../hooks/useAuth';

type SignPetitionButtonProps = {
  petitionID: number;
  disabled: boolean;
  onSignChange: (id: number, total_signatures: number) => void;
};

export default function SignPetitionButton({
  petitionID,
  disabled,
  onSignChange,
}: SignPetitionButtonProps) {
  const [signed, setSigned] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);
  const [ownPetition, setOwnPetition] = useState(false)
  const [signingDisabled, setSigningDisabled] = useState<boolean>(disabled);
  const { logIn } = useAuth();

  
  // On mount, check whether the current user has signed this petition
  
  useEffect(() => {
    if (!petitionID || signingDisabled) return;

    const fetchSignedState = async () => {
      setLoading(true)
      try {
        const res = await fetch(
          `${API_URL}/api/v1/users/${petitionID}/can_sign`,
          {
            method: 'GET',
            credentials: 'include',
          }
        );

        if (res.status === 200 || res.status === 401) {
          return;
        } else {
          setButtonLabel(res)
        }

      } catch (err) {
        console.error('Error checking signed state:', err);
        setSigned(false);
      } finally {
        setLoading(false)
      }
    };

    fetchSignedState();
  }, [petitionID]);

  const handleClick = async () => {
    if (!petitionID || signingDisabled || loading) return;
  
    setLoading(true);
    try {
      if (!signed) {
        // SIGN
        const res = await fetch(`${API_URL}/api/v1/users/${petitionID}/sign`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        setButtonLabel(res);
      } else {
        // UNSIGN
        const res = await fetch(
          `${API_URL}/api/v1/users/${petitionID}/unsign`,
          {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        setButtonLabel(res);
      }
    } catch (err) {
      console.error('Error while signing/unsigning:', err);
    } finally {
      setLoading(false);
    }
  };

  const setButtonLabel = async (response: Response) => {
    const body = await response.json()

    switch(response.status) {
      case 200:
        setSigned(body.signed);
        setSigningDisabled(false);
        onSignChange(petitionID, body.total_signatures);
        return;
      case 401:
        logIn(`petition=${petitionID}`);
        return;
      case 404:
        if (body.message) alert(body.message);
        setSigningDisabled(true);
        return;
      case 409:
        setSigned(true);
        return;
      case 423:
        setOwnPetition(true);
        return;
      default:
        console.error(
            `Error with Petition Signing`,
            response.status
          );
        setSigned(false);
        return;
    }

  }

  const getButtonLabel = () => {
    if (ownPetition) return "Owned Petition";
    if (signingDisabled) return 'Signing Closed';
    if (loading) return 'Please wait...';
    if (signed) return 'Unsign';
    return 'Sign this Petition';
  };

  return (
    <Button
      type="button"
      onClick={handleClick}
      variant="highlight"
      disabled={loading || signingDisabled}
    >
      {getButtonLabel()}
    </Button>
  );
}
