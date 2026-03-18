import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { Loader2, User as UserIcon, Mail, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/api/client';
import { useAuth } from '@/components/auth/AuthContext';
import type { User } from '@/api/auth';

const editProfileSchema = z.object({
  first_name: z
    .string()
    .min(2, 'Imię musi mieć co najmniej 2 znaki')
    .max(50, 'Imię nie może być dłuższe niż 50 znaków'),
  last_name: z
    .string()
    .min(2, 'Nazwisko musi mieć co najmniej 2 znaki')
    .max(50, 'Nazwisko nie może być dłuższe niż 50 znaków'),
  email: z
    .string()
    .min(1, 'Email jest wymagany')
    .email('Podaj prawidłowy adres email'),
  location: z
    .string()
    .max(200, 'Lokalizacja nie może być dłuższa niż 200 znaków')
    .optional(),
});

type EditProfileFormData = z.infer<typeof editProfileSchema>;

interface EditProfileFormProps {
  user: User;
  onSuccess?: () => void;
}

export function EditProfileForm({ user, onSuccess }: EditProfileFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { user: _authUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
  } = useForm<EditProfileFormData>({
    resolver: zodResolver(editProfileSchema),
    defaultValues: {
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      location: user.location || '',
    },
  });

  const onSubmit = async (data: EditProfileFormData) => {
    setIsLoading(true);
    
    try {
      const response = await api.patch<{ success: boolean; data?: { user: User }; error?: string }>(
        '/users/me',
        data
      );

      if (response.success) {
        toast.success('Profil został zaktualizowany', {
          description: 'Twoje dane zostały pomyślnie zmienione.',
        });
        
        // Reset form with new values
        reset(data);
        onSuccess?.();
      } else {
        toast.error('Błąd aktualizacji', {
          description: response.error || 'Nie udało się zaktualizować profilu.',
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Wystąpił nieoczekiwany błąd';
      toast.error('Błąd aktualizacji', {
        description: message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-2">
        {/* First Name */}
        <div className="space-y-2">
          <Label htmlFor="first_name" className="text-book-brown">
            <UserIcon className="w-4 h-4 inline mr-2" />
            Imię
          </Label>
          <Input
            id="first_name"
            {...register('first_name')}
            className={errors.first_name ? 'border-red-500' : ''}
            disabled={isLoading}
          />
          {errors.first_name && (
            <p className="text-sm text-red-500">{errors.first_name.message}</p>
          )}
        </div>

        {/* Last Name */}
        <div className="space-y-2">
          <Label htmlFor="last_name" className="text-book-brown">
            <UserIcon className="w-4 h-4 inline mr-2" />
            Nazwisko
          </Label>
          <Input
            id="last_name"
            {...register('last_name')}
            className={errors.last_name ? 'border-red-500' : ''}
            disabled={isLoading}
          />
          {errors.last_name && (
            <p className="text-sm text-red-500">{errors.last_name.message}</p>
          )}
        </div>
      </div>

      {/* Email */}
      <div className="space-y-2">
        <Label htmlFor="email" className="text-book-brown">
          <Mail className="w-4 h-4 inline mr-2" />
          Email
        </Label>
        <Input
          id="email"
          type="email"
          {...register('email')}
          className={errors.email ? 'border-red-500' : ''}
          disabled={isLoading}
        />
        {errors.email && (
          <p className="text-sm text-red-500">{errors.email.message}</p>
        )}
        <p className="text-xs text-book-muted">
          Zmiana adresu email może wymagać ponownej weryfikacji.
        </p>
      </div>

      {/* Location */}
      <div className="space-y-2">
        <Label htmlFor="location" className="text-book-brown">
          <MapPin className="w-4 h-4 inline mr-2" />
          Lokalizacja (miasto)
        </Label>
        <Input
          id="location"
          placeholder="np. Warszawa"
          {...register('location')}
          className={errors.location ? 'border-red-500' : ''}
          disabled={isLoading}
        />
        {errors.location && (
          <p className="text-sm text-red-500">{errors.location.message}</p>
        )}
        <p className="text-xs text-book-muted">
          Twoja lokalizacja będzie widoczna przy książkach, które udostępniasz.
        </p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4 pt-4">
        <Button
          type="submit"
          className="bg-book-gold hover:bg-book-gold-hover"
          disabled={isLoading || !isDirty}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Zapisywanie...
            </>
          ) : (
            'Zapisz zmiany'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => reset()}
          disabled={isLoading || !isDirty}
        >
          Anuluj
        </Button>
      </div>
    </form>
  );
}
